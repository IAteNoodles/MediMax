# MediMax Noodles Backend

This directory contains the core intelligent backend services for the MediMax application, codenamed "Noodles". It consists of two main components that work in tandem: a conversational AI agent (`chat_api.py`) and a powerful tool server (`mcp_server.py`) that provides the agent with its capabilities.

The system is designed to interact with a user, understand complex medical queries, access and process data from multiple databases (SQL and Graph), and even call specialized machine learning models for risk prediction.

## Tech Stack

- **Web Framework**: `FastAPI` (for both the chat API and the MCP server)
- **Conversational AI**: `LangChain`
- **Language Model (LLM)**: Google `Gemini 1.5 Flash` via `langchain-google-genai`
- **Tooling Protocol**: `MCP (Model-Context-Protocol)` via `fastmcp` and `langchain-mcp-adapters`
- **Databases**:
  - **Relational**: `MySQL` (for storing atomic patient facts)
  - **Graph**: `Neo4j` (for storing a patient knowledge graph)
- **Machine Learning**: The server is capable of calling external `scikit-learn` and `PyTorch` models served via local APIs.
- **Configuration**: `python-dotenv` for environment variable management.

---

## Architecture Overview

The architecture is composed of two microservices:

1.  **Chat API (`chat_api.py`)**: This is the user-facing entry point. It exposes a `/chat` endpoint that receives natural language queries. It initializes a LangChain agent powered by Google's Gemini model. This agent's primary role is to understand the user's request and decide which tool to use to fulfill it.

2.  **MCP Server (`mcp_server.py`)**: This server acts as the "toolbox" for the LangChain agent. It exposes a collection of functions as tools using the Model-Context-Protocol (MCP). These tools are the agent's "hands and eyes," allowing it to perform actions like querying databases, creating knowledge graphs, and calling ML models.

The flow is as follows:
- A user sends a message to the **Chat API**.
- The LangChain agent in the Chat API receives the message.
- The agent determines the user's intent and selects an appropriate tool from the **MCP Server**.
- The agent calls the tool on the MCP Server with the necessary parameters.
- The MCP Server executes the tool's logic (e.g., queries the Neo4j database).
- The result is returned to the agent.
- The agent uses the tool's output and the LLM to formulate a natural language response to the user.

---

## Components

### 1. Chat API (`chat_api.py`)

This FastAPI application serves as the brain of the operation.

- **Agent Initialization**: On startup, it initializes a `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION` agent. This agent type is specifically chosen for its ability to work with tools that require structured (JSON) inputs, which is essential for the complex medical tools provided by the MCP server.
- **Tool Fetching**: It dynamically fetches its available tools from the MCP server running at `http://127.0.0.1:8005`. This decouples the agent's logic from the tool's implementation.
- **LLM Integration**: It uses the `gemini-1.5-flash` model from Google for its reasoning capabilities.
- **Endpoint**:
  - `POST /chat`: Accepts a JSON with a `message` key. It invokes the agent with the message and returns the agent's final response.
- **Execution**: Runs on `http://0.0.0.0:8000`.

### 2. MCP Server (`mcp_server.py`)

This `FastMCP` server is the workhorse, providing all the capabilities for the agent. It connects to both a MySQL database for raw data and a Neo4j database for the knowledge graph.

#### Key Feature: Knowledge Graph Creation

The most significant feature of this server is its ability to dynamically create a patient-centric knowledge graph.

- **`Create_Knowledge_Graph(patient_id: int)`**: This tool triggers a multi-step process:
  1.  It fetches all data related to a `patient_id` from the `MySQL` database (demographics, medical history, medications, appointments, symptoms, lab reports).
  2.  It processes this relational data and transforms it into a graph structure.
  3.  It connects to the `Neo4j` database, clears any old data for that patient, and creates a new, rich knowledge graph.
  4.  The graph consists of nodes like `Patient`, `Condition`, `Medication`, `Symptom`, `Encounter`, and `LabResult`, with meaningful relationships (`HAS_CONDITION`, `TAKES_MEDICATION`, `MAY_INDICATE`) connecting them.

#### Exposed Tools

The server exposes the following functions as tools for the LangChain agent:

- **Knowledge Graph Tools**:
  - `Create_Knowledge_Graph(patient_id: int)`: Builds the graph for a patient.
  - `Run_Cypher_Query(cypher: str)`: Executes a raw Cypher query on the Neo4j database.
  - `Validate_Graph_Connectivity()`: Checks the integrity of the graph.

- **Machine Learning Model Tools**:
  - `Predict_Cardiovascular_Risk_With_Explanation(...)`: Calls a local API (at `http://localhost:5002`) to predict cardiovascular risk based on patient metrics.
  - `Predict_Diabetes_Risk_With_Explanation(...)`: Calls a local API (at `http://localhost:5003`) to predict diabetes risk.

- **Database & Backend Tools**:
  - `Get_Patient_Details(patient_id: str)`: Fetches basic patient info.
  - `Get_Patient_Symptoms(patient_id: int)`: Retrieves a patient's symptoms.
  - `Get_Patient_Medical_Reports(patient_id: int)`: Fetches lab and medical reports.
  - `New_Patient(name: str, age: int)`: Adds a new patient.
  - `Health_Check()`: Checks the health of the dependent `backend_abhishek` service.

- **Execution**: Runs on `http://0.0.0.0:8005`.

---

## Setup and How to Run

1.  **Environment Variables**: Ensure a `.env` file exists in the parent directory (`MediMax/`) with the following keys:
    - `GOOGLE_API_KEY`
    - `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (for MySQL)
    - `NEO4J_URI`, `AURA_USER`, `AURA_PASSWORD` (for Neo4j)
    - `BACKEND_ABHISHEK_URL`

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Services**: You need to run both services in separate terminals.

    - **Terminal 1: Start the MCP Tool Server**
      ```bash
      python mcp_server.py
      ```
      *This will start the server on port 8005.*

    - **Terminal 2: Start the Chat API**
      ```bash
      python chat_api.py
      ```
      *This will start the server on port 8000. On startup, it will connect to the MCP server and fetch the tools.*

4.  **Interact with the API**: You can now send `POST` requests to `http://127.0.0.1:8000/chat` with a JSON payload to interact with the agent.

    **Example Request:**
    ```json
    {
      "message": "Create a knowledge graph for patient 123 and then tell me what medications they are on."
    }
    ```