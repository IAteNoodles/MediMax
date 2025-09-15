# MediMax Agentic Orchestration and Frontend

This directory, `Anugrah`, contains two major, interconnected components of the MediMax project: a sophisticated multi-agent system for medical assessment (`agents`) and a modern React-based user interface (`front-end`).

## Table of Contents

1.  [Overall Architecture](#-overall-architecture)
2.  [Agents Sub-directory](#-agents-sub-directory)
    -   [Tech Stack](#tech-stack-agents)
    -   [Core Functionality](#core-functionality-agents)
    -   [Key Components](#key-components-agents)
    -   [Setup and How to Run](#setup-and-how-to-run-agents)
3.  [Front-end Sub-directory](#-front-end-sub-directory)
    -   [Tech Stack](#tech-stack-front-end)
    -   [Core Functionality](#core-functionality-front-end)
    -   [Key Components](#key-components-front-end)
    -   [Setup and How to Run](#setup-and-how-to-run-front-end)

---

## 🏗️ Overall Architecture

The `Anugrah` folder houses the "brains" and the "face" of the advanced AI features of MediMax.

-   The **`agents`** system acts as an intelligent orchestration layer. It receives unstructured patient data, uses a series of LLM-powered agents to understand the context, identify the required medical models, gather necessary parameters, and generate a comprehensive report.
-   The **`front-end`** provides a polished, user-friendly web interface for doctors and clinicians to interact with the MediMax system, view patient data, and use the agentic assessment tools.

```
┌──────────────────┐      ┌──────────────────────────┐      ┌──────────────────┐
│   Front-end UI   │◄───► │   Agent API Server       │◄───► │   MCP Server     │
│ (React, Vite)    │      │   (FastAPI, LangGraph)   │      │ (ML Models)      │
└──────────────────┘      └──────────────────────────┘      └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │   LLM Services   │
                             │   (Groq, Ollama) │
                             └──────────────────┘
```

---

## 🤖 Agents Sub-directory

This directory contains a multi-agent medical assessment system built with Python, FastAPI, and LangGraph.

### Tech Stack (Agents)

-   **Orchestration Framework**: `LangGraph`
-   **Web Server**: `FastAPI`
-   **LLM Providers**: `Groq` (for agentic logic), `Ollama` (for summarization via `MedGemma`)
-   **Core Libraries**: `langchain-core`, `pydantic`, `httpx`
-   **Demo/UI**: `Streamlit`
-   **Configuration**: `python-dotenv`

### Core Functionality (Agents)

This system is designed to intelligently handle complex medical assessment queries from unstructured text.

1.  **Text Understanding (Main Agent)**: The system first receives a block of text describing a patient's condition. A "Main Agent" (powered by a Groq LLM) reads this text, summarizes the clinical situation, extracts structured data (like age, blood pressure), and formulates a high-level plan.

2.  **Model Routing (Router Agent)**: Based on the Main Agent's plan, a "Router Agent" takes over. It determines which specific ML prediction models (e.g., cardiovascular risk, diabetes risk) are relevant to the query.

3.  **Iterative Data Gathering**: The Router Agent checks if it has all the necessary parameters to run the selected models. If not, it returns a `need_more_data` status, listing exactly which parameters are missing. The user or calling system can then provide the missing data and re-run the assessment.

4.  **Model Execution (MCP Integration)**: Once all required parameters are available, the agent system calls an external **MCP (Model-Context-Protocol) Server** to execute the ML models and get predictions.

5.  **Report Generation**: The final results, including model predictions, explanations, and the LLM's own reasoning, are compiled into a comprehensive report.

### Key Components (Agents)

-   **`api_server.py`**: The main production entry point. A FastAPI server that exposes the agentic system via a REST API. Key endpoints include `/assess`, `/assess/cardiovascular`, and `/models`.
-   **`app.py`**: A Streamlit application that provides a user-friendly interface for demonstrating and debugging the agentic system without needing a full backend.
-   **`medimax/graph.py`**: The heart of the system. It uses `LangGraph` to define the state machine and the flow between the `main_agent_node` and the `router_agent_node`.
-   **`medimax/agents/`**: Contains the specific logic and prompts for the `MainAgent` and `RouterAgent`.
-   **`medimax/llm/`**: Contains clients for interacting with LLM providers like Groq.
-   **`medimax/mcp/`**: Contains the client for communicating with the external MCP server where ML models are hosted.

### Setup and How to Run (Agents)

1.  **Environment Variables**: Create a `.env` file in the `Anugrah/agents/` directory. It must contain your Groq API key.
    ```
    GROQ_API_KEY="gsk_..."
    MCP_BASE_URL="http://<address_of_mcp_server>"
    MEDGEMMA_BASE_URL="http://<address_of_ollama_server>"
    ```

2.  **Install Dependencies**:
    ```bash
    cd Anugrah/agents
    pip install -r requirements.txt
    ```

3.  **Run the API Server**:
    ```bash
    python api_server.py
    ```
    The API will be available at `http://localhost:8000` with documentation at `http://localhost:8000/docs`.

4.  **(Optional) Run the Streamlit Demo App**:
    ```bash
    streamlit run app.py
    ```

---

## 🖥️ Front-end Sub-directory

This directory contains a modern, single-page application (SPA) built with React to serve as the user interface for the MediMax platform.

### Tech Stack (Front-end)

-   **Framework**: `React`
-   **Build Tool**: `Vite`
-   **Routing**: `React Router`
-   **Styling**: `Tailwind CSS`
-   **Language**: `JavaScript (JSX)`

### Core Functionality (Front-end)

-   **User Authentication**: A login page to secure access to the dashboard.
-   **Patient Dashboard**: Displays a list of patients, allowing clinicians to quickly find and select a patient.
-   **Patient Detail View**: Shows a comprehensive view of a selected patient's medical records.
-   **Agentic Interface**: A dedicated interface (`/agentic-interface`) for interacting with the powerful AI assessment tools provided by the `agents` backend.

### Key Components (Front-end)

-   **`src/App.jsx`**: The main application component that sets up the routing for the entire site.
-   **`src/components/`**: Contains all the reusable React components.
    -   `Login.jsx`: The login form.
    -   `Dashboard.jsx`: The main patient list view after login.
    -   `PatientDetail.jsx`: The detailed view for a single patient.
    -   `AgenticInterface.jsx`: The UI for the AI assessment feature.
-   **`src/main.jsx`**: The entry point for the React application.
-   **`vite.config.js`**: Configuration file for the Vite build tool.
-   **`tailwind.config.js`**: Configuration for the Tailwind CSS framework.

### Setup and How to Run (Front-end)

1.  **Install Dependencies**:
    ```bash
    cd Anugrah/front-end
    npm install
    ```

2.  **Run the Development Server**:
    ```bash
    npm run dev
    ```
    The front-end application will be available at `http://localhost:5173` (or another port if 5173 is busy).

3.  **Build for Production**:
    ```bash
    npm run build
    ```
    This will create a `dist` folder with the optimized, static assets ready for deployment.
