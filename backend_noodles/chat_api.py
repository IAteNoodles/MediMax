import os
import asyncio
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import BaseTool
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Assuming this is your custom client for fetching tools.
# Make sure this library is installed in your environment.
from langchain_mcp_adapters.client import MultiServerMCPClient

# --- Configuration Loading ---
# It's good practice to load environment variables at the start.
# This ensures the application fails fast if configuration is missing.
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Get Google API key from environment variables
google_api_key = os.getenv('GOOGLE_API_KEY')
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file")


# --- Tool Fetching ---
# This async function fetches the tools required by the LangChain agent.
async def get_mcp_tools() -> List[BaseTool]:
    """
    Asynchronously initializes the MultiServerMCPClient and fetches tools.
    """
    # This configuration points to a local service that provides the tools.
    client = MultiServerMCPClient(
        {
            "Hospital": {
                "url": "http://127.0.0.1:8005/mcp/",
                "transport": "streamable_http"
            }
        }
    )
    print("Fetching tools from MCP server...")
    tools = await client.get_tools()
    print(f"Successfully fetched {len(tools)} tools.")
    return tools

# --- Application State Management ---
# A dictionary to hold application-level state, like the initialized agent.
# This avoids using global variables directly.
app_state = {}


# --- FastAPI Lifespan Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the FastAPI application.
    """
    # --- Startup Logic ---
    print("Application starting up...")
    tools = await get_mcp_tools()

    # Updated to the model you requested
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=google_api_key)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Initialize the LangChain agent
    # Switched to STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, which is designed
    # to handle tools that require structured JSON inputs. This fixes the error.
    agent = initialize_agent(
        tools=tools,
        llm=model,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )

    app_state["agent"] = agent
    print("Agent initialized and ready.")

    yield  # The application is now running

    # --- Shutdown Logic ---
    print("Application shutting down...")
    app_state.clear()
    print("Resources cleaned up.")


# --- FastAPI App Initialization ---
app = FastAPI(
    title="LangChain Chat API",
    description="An API for interacting with a conversational agent.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    message: str


# --- Dependency Injection for Agent ---
def get_agent() -> AgentExecutor:
    """
    FastAPI dependency to get the agent from the application state.
    """
    if "agent" not in app_state:
        raise HTTPException(status_code=500, detail="Agent is not initialized.")
    return app_state["agent"]


# --- API Endpoint ---
@app.post("/chat")
async def chat(
    request: ChatRequest,
    agent: AgentExecutor = Depends(get_agent)
):
    """
    Receives a message, processes it with the LangChain agent, and returns the response.
    """
    try:
        # Kept the asynchronous `ainvoke` method to prevent the "sync invocation" error
        # with the StructuredTool.
        result = await agent.ainvoke({"input": request.message})
        response = result.get("output", "Sorry, I encountered an issue and couldn't respond.")
        return {"response": response}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Main Execution Block ---
if __name__ == "__main__":
    import uvicorn
    import socket

    def get_local_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't actually send data; used to determine default outbound interface IP
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    port = 8000
    host = "0.0.0.0"
    local_ip = get_local_ip()

    print(f"Starting server:")
    print(f"  Local:   http://127.0.0.1:{port}")
    print(f"  Network: http://{local_ip}:{port} (accessible from LAN when host is reachable)")

    uvicorn.run(app, host=host, port=port, log_level="debug")

