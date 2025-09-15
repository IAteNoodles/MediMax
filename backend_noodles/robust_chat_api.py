"""
Robust Chat API Framework with Enhanced Tool Calling and Error Recovery
----------------------------------------------------------------------
This module provides a robust framework for LangChain agent integration
with proper tool calling, error handling, and retry mechanisms.
"""

import os
import asyncio
import logging
import traceback
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import BaseTool
from langchain_core.prompts import PromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://127.0.0.1:8005/mcp/')

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

class AgentStatus(Enum):
    """Agent status enumeration"""
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    BUSY = "busy"

class ChatRequest(BaseModel):
    """Enhanced chat request model with metadata"""
    message: str = Field(..., description="User message to process")
    session_id: Optional[str] = Field(None, description="Session identifier for conversation continuity")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the request")
    max_retries: Optional[int] = Field(3, description="Maximum number of retries for failed operations")

class ChatResponse(BaseModel):
    """Enhanced chat response model with metadata"""
    response: str = Field(..., description="Agent response")
    session_id: Optional[str] = Field(None, description="Session identifier")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = Field(default="success")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    tools_used: Optional[List[str]] = Field(None, description="List of tools used in processing")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    agent_status: str
    tools_count: int
    uptime_seconds: float
    last_error: Optional[str] = None

class AgentState:
    """Enhanced agent state management"""
    def __init__(self):
        self.status = AgentStatus.INITIALIZING
        self.agent: Optional[AgentExecutor] = None
        self.tools: List[BaseTool] = []
        self.error_count = 0
        self.last_error: Optional[str] = None
        self.startup_time: Optional[datetime] = None

# Global application state
app_state = AgentState()

class RobustMCPClient:
    """Robust MCP client with error handling and retry logic"""
    
    def __init__(self, server_configs: Dict[str, Dict[str, str]], max_retries: int = 3):
        self.server_configs = server_configs
        self.max_retries = max_retries
        self.client: Optional[MultiServerMCPClient] = None
        
    async def initialize(self) -> bool:
        """Initialize MCP client with retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.client = MultiServerMCPClient(self.server_configs)
                logger.info(f"MCP client initialized successfully on attempt {attempt + 1}")
                return True
            except Exception as e:
                logger.warning(f"MCP client initialization attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to initialize MCP client after {self.max_retries} attempts")
                    return False
        return False
    
    async def get_tools(self) -> List[BaseTool]:
        """Get tools with error handling and validation"""
        if not self.client:
            raise RuntimeError("MCP client not initialized")
            
        for attempt in range(self.max_retries):
            try:
                tools = await self.client.get_tools()
                logger.info(f"Successfully fetched {len(tools)} tools from MCP server")
                
                # Validate tools
                validated_tools = self._validate_tools(tools)
                logger.info(f"Validated {len(validated_tools)} tools")
                return validated_tools
                
            except Exception as e:
                logger.warning(f"Tool fetching attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    logger.error(f"Failed to fetch tools after {self.max_retries} attempts")
                    raise
        return []
    
    def _validate_tools(self, tools: List[BaseTool]) -> List[BaseTool]:
        """Validate and filter tools"""
        validated_tools = []
        for tool in tools:
            try:
                # Basic validation
                if hasattr(tool, 'name') and hasattr(tool, 'description'):
                    validated_tools.append(tool)
                    logger.debug(f"Validated tool: {tool.name}")
                else:
                    logger.warning(f"Invalid tool structure: {tool}")
            except Exception as e:
                logger.warning(f"Tool validation error: {e}")
        return validated_tools

class RobustAgentManager:
    """Robust agent management with enhanced error handling"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.llm: Optional[ChatGoogleGenerativeAI] = None
        self.memory: Optional[ConversationBufferMemory] = None
        
    async def initialize_agent(self, tools: List[BaseTool]) -> AgentExecutor:
        """Initialize agent with robust configuration"""
        try:
            # Initialize LLM with specific parameters for tool calling
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                api_key=self.api_key,
                temperature=0.1,  # Lower temperature for more consistent tool calling
                max_tokens=2048,
                timeout=30
            )
            
            # Initialize memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="output"
            )
            
            # Create custom prompt template for React agent
            prompt_template = """
You are a helpful medical AI assistant with access to specialized tools for patient data and medical predictions.

AVAILABLE TOOLS:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT: For Run_Cypher_Query tool, provide the Action Input as a JSON object:
{{"cypher": "MATCH (p:Patient {{patient_id: 20}})-[:TAKES_MEDICATION]->(m:Medication) RETURN m.name AS medication_name"}}

Begin!

Previous conversation history:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}"""
            
            prompt = PromptTemplate.from_template(prompt_template)
            
            # Create React agent
            agent = create_react_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt
            )
            
            # Create agent executor with error handling
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=self.memory,
                verbose=True,
                max_iterations=5,
                return_intermediate_steps=True,
                handle_parsing_errors=True
            )
            
            logger.info(f"Agent initialized with {len(tools)} tools")
            return agent_executor
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize agent: {str(e)}")

async def initialize_robust_chat_system():
    """Initialize the robust chat system with error handling"""
    try:
        app_state.startup_time = datetime.now()
        app_state.status = AgentStatus.INITIALIZING
        
        # Initialize MCP client
        mcp_client = RobustMCPClient({
            "Hospital": {
                "url": MCP_SERVER_URL,
                "transport": "streamable_http"
            }
        })
        
        # Initialize client and get tools
        if not await mcp_client.initialize():
            raise RuntimeError("Failed to initialize MCP client")
        
        tools = await mcp_client.get_tools()
        app_state.tools = tools
        
        # Initialize agent manager
        agent_manager = RobustAgentManager(GOOGLE_API_KEY)
        agent = await agent_manager.initialize_agent(tools)
        
        app_state.agent = agent
        app_state.status = AgentStatus.READY
        
        logger.info(f"Robust chat system initialized successfully with {len(tools)} tools")
        return True
        
    except Exception as e:
        app_state.status = AgentStatus.ERROR
        app_state.last_error = str(e)
        app_state.error_count += 1
        logger.error(f"Failed to initialize robust chat system: {e}")
        traceback.print_exc()
        return False

async def process_chat_with_retry(request: ChatRequest) -> ChatResponse:
    """Process chat with retry logic and error handling"""
    if app_state.status != AgentStatus.READY or not app_state.agent:
        raise HTTPException(status_code=503, detail="Agent not ready")
    
    max_retries = request.max_retries or 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            app_state.status = AgentStatus.BUSY
            
            # Prepare input with context
            agent_input = {
                "input": request.message,
                "chat_history": app_state.agent.memory.chat_memory.messages if app_state.agent.memory else []
            }
            
            # Add context if provided
            if request.context:
                agent_input["context"] = request.context
            
            # Execute agent
            result = await app_state.agent.ainvoke(agent_input)
            
            app_state.status = AgentStatus.READY
            
            # Extract tools used (if available in result)
            tools_used = []
            if hasattr(result, 'intermediate_steps'):
                tools_used = [step[0].tool for step in result.get('intermediate_steps', [])]
            
            return ChatResponse(
                response=result.get("output", "I apologize, but I couldn't generate a response."),
                session_id=request.session_id,
                status="success",
                metadata={
                    "attempt": attempt + 1,
                    "agent_status": app_state.status.value
                },
                tools_used=tools_used
            )
            
        except Exception as e:
            last_error = str(e)
            app_state.error_count += 1
            app_state.last_error = last_error
            
            logger.warning(f"Chat processing attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                await asyncio.sleep(1)  # Brief delay before retry
            else:
                app_state.status = AgentStatus.ERROR
                logger.error(f"Chat processing failed after {max_retries} attempts: {last_error}")
    
    app_state.status = AgentStatus.READY  # Reset status
    raise HTTPException(
        status_code=500, 
        detail=f"Chat processing failed after {max_retries} attempts. Last error: {last_error}"
    )

# FastAPI Application Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced lifespan management with robust initialization"""
    logger.info("Starting robust chat API...")
    
    # Initialize the robust chat system
    success = await initialize_robust_chat_system()
    
    if not success:
        logger.error("Failed to initialize chat system")
        # You might want to exit or implement fallback behavior here
    
    yield
    
    # Cleanup
    logger.info("Shutting down robust chat API...")
    app_state.status = AgentStatus.ERROR
    if app_state.agent and hasattr(app_state.agent, 'memory'):
        app_state.agent.memory.clear()

# Create FastAPI app
app = FastAPI(
    title="Robust MediMax Chat API",
    description="Enhanced chat API with robust tool calling and error recovery",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Enhanced health check with detailed status"""
    uptime = 0
    if app_state.startup_time:
        uptime = (datetime.now() - app_state.startup_time).total_seconds()
    
    return HealthResponse(
        status="healthy" if app_state.status == AgentStatus.READY else "unhealthy",
        agent_status=app_state.status.value,
        tools_count=len(app_state.tools),
        uptime_seconds=uptime,
        last_error=app_state.last_error
    )

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Enhanced chat endpoint with robust processing"""
    try:
        return await process_chat_with_retry(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Reset agent endpoint (for debugging)
@app.post("/reset")
async def reset_agent():
    """Reset the agent (useful for debugging)"""
    try:
        success = await initialize_robust_chat_system()
        return {"status": "success" if success else "failed", "message": "Agent reset completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reset failed: {str(e)}")

# Main execution
if __name__ == "__main__":
    import uvicorn
    import socket

    def get_local_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
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

    print(f"Starting Robust MediMax Chat API:")
    print(f"  Local:   http://127.0.0.1:{port}")
    print(f"  Network: http://{local_ip}:{port}")
    print(f"  Health:  http://127.0.0.1:{port}/health")
    print(f"  Docs:    http://127.0.0.1:{port}/docs")

    uvicorn.run(app, host=host, port=port, log_level="info")