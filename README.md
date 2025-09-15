# MediMax - AI-Powered Healthcare Management System

Welcome to the MediMax project! This is a comprehensive, multi-module healthcare platform designed to manage patient data, provide advanced medical analysis through AI, and offer a modern user interface for clinicians.

## 🚀 Project Overview

MediMax is not a single application but a suite of interconnected services that work together to provide a powerful healthcare management solution. The system is built around a microservices architecture, with each major folder in this repository representing a distinct service or component.

### Core Features
- **Comprehensive Patient Data Management**: Full CRUD capabilities for patient records, appointments, medications, and lab reports via a relational database.
- **Advanced AI Orchestration**: A sophisticated multi-agent system that understands unstructured patient data, selects appropriate ML models, and generates detailed medical assessments.
- **Knowledge Graph Integration**: Dynamically builds and queries a Neo4j knowledge graph from patient data to uncover complex relationships and insights.
- **Machine Learning Model Serving**: A dedicated service to host and serve predictive models (e.g., for cardiovascular and diabetes risk).
- **Modern User Interface**: A React-based frontend for clinicians to interact with patient data and AI tools.

---

## 🏛️ System Architecture

The project is divided into several key modules, each with a specific role:

```
┌──────────────────┐      ┌──────────────────────────┐      ┌──────────────────┐
│   Anugrah        │      │     backend_abhishek     │      │   backend_noodles  │
│  (Frontend &     │◄───► │   (Main API & DB Layer)  │◄───► │  (Agent & MCP     │
│   Agent Logic)   │      │                          │      │   Tool Server)   │
└──────────────────┘      └──────────────────────────┘      └──────────────────┘
         │                        │          │                      │
         ▼                        ▼          ▼                      ▼
┌──────────────────┐      ┌──────────┐   ┌─────────┐      ┌──────────────────┐
│   LLM Services   │      │  MariaDB │   │  Neo4j  │      │    AI_Models     │
│   (Groq/Ollama)  │      │ (Patient │   │ (Graph) │      │   (ML Model APIs)  │
└──────────────────┘      └──────────┘   └─────────┘      └──────────────────┘
```

### Module Descriptions

-   **`Anugrah/`**: Contains the "brains" and "face" of the application.
    -   **`agents/`**: A `LangGraph`-based multi-agent system for intelligent medical assessment.
    -   **`front-end/`**: The `React` and `Vite` powered user interface.
-   **`backend_abhishek/`**: The primary backend service. It's a `FastAPI` application that manages all CRUD operations with the `MariaDB` database and acts as a proxy to other services.
-   **`backend_noodles/`**: The core AI and tooling service.
    -   **`mcp_server.py`**: A `FastMCP` server that exposes tools (like database queries and ML model calls) to the AI agents.
    -   **`chat_api.py`**: A `LangChain` agent that uses the tools from the MCP server to answer complex questions.
-   **`AI_Models/`**: Contains the machine learning models (e.g., `XGBoost` for cardiovascular and diabetes risk) and the `FastAPI` servers to expose them as APIs.
-   **`Database_Schema_README.md`**: Detailed documentation of the `MariaDB/MySQL` relational schema.
-   **`NEO4J_RELATIONSHIP_SCHEMA.md`**: Documentation for the `Neo4j` graph schema.

---

## 🛠️ Installation and Setup

Follow these steps to get the entire MediMax ecosystem running.

### 1. Prerequisites
- Python 3.8+
- Node.js and npm (for the frontend)
- Docker (optional, for running ML models)
- Access to MariaDB/MySQL and Neo4j databases.
- A Groq API key for the agentic system.

### 2. Global Setup

**a. Clone the Repository**
```bash
git clone <repository-url>
cd MediMax
```

**b. Create the Global Environment File**
Create a file named `.env` in the root `MediMax/` directory. This file will hold all the secrets and configurations for the different services.

```env
# --- Database Credentials ---
# MariaDB/MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medimax
DB_USER=your_username
DB_PASSWORD=your_password

# Neo4j Aura
NEO4J_URI=neo4j+s://your-neo4j-instance.databases.neo4j.io
AURA_USER=neo4j
AURA_PASSWORD=your_neo4j_password

# --- AI Service Keys & URLs ---
# Groq (for agentic logic)
GROQ_API_KEY="gsk_..."

# Google (if using Gemini models)
GOOGLE_API_KEY="your_google_api_key"

# --- Service URLs (adjust if running on different machines/ports) ---
AGENTIC_ADDRESS=http://127.0.0.1:8000
BACKEND_ABHISHEK_URL=http://127.0.0.1:8821
MCP_SERVER_URL=http://127.0.0.1:8005
CARDIO_API_URL=http://127.0.0.1:5002
DIABETES_API_URL=http://127.0.0.1:5003
```

**c. Install All Python Dependencies**
This project uses a single `requirements.txt` file in the root directory for simplicity.
```bash
pip install -r requirements.txt
```

### 3. Running the Services

You will need to run each service in a separate terminal.

**Terminal 1: Start the ML Model APIs (Cardio & Diabetes)**
```bash
cd AI_Models/cardio
python cardiovascular_api.py
```
In another terminal:
```bash
cd AI_Models/diabetes
python diabetes_api.py
```

**Terminal 2: Start the `backend_noodles` MCP Server**
This server provides tools to the AI agent.
```bash
cd backend_noodles
python mcp_server.py
```

**Terminal 3: Start the `backend_abhishek` Main API**
This is the main data layer.
```bash
cd backend_abhishek
python app.py
```

**Terminal 4: Start the `Anugrah` Agentic API Server**
This server exposes the intelligent agent.
```bash
cd Anugrah/agents
python api_server.py
```

**Terminal 5: Start the `Anugrah` Frontend**
```bash
cd Anugrah/front-end
npm install
npm run dev
```

🎉 Your MediMax ecosystem is now running!
-   **Frontend**: `http://localhost:5173`
-   **Main Backend API**: `http://localhost:8821`
-   **Agentic API**: `http://localhost:8000`

---

## 🗄️ Database Schemas

### Relational Database (MariaDB/MySQL)

The relational database is the source of truth for atomic patient data.

-   **`Patient`**: Central table with patient demographics.
-   **`Medical_History`**: Chronic conditions, allergies, surgeries.
-   **`Appointment`**: Records of patient visits.
-   **`Medication`**: Prescribed medications.
-   **`Lab_Report`** & **`Lab_Finding`**: Detailed lab results.

**Key Relationships**:
- `Patient` (1:N) → `Medical_History`, `Appointment`, `Medication`, `Lab_Report`
- `Appointment` (1:N) → `Appointment_Symptom`
- `Lab_Report` (1:N) → `Lab_Finding`

### Knowledge Graph (Neo4j)

The knowledge graph is dynamically built from the relational data to represent complex connections.

-   **Nodes**: `Patient`, `Symptom`, `Condition`, `Medication`, `Encounter`, `LabResult`.
-   **Relationships**: `HAS_SYMPTOM`, `TAKES_MEDICATION`, `HAS_CONDITION`, `TREATS_CONDITION`, `MAY_INDICATE`.

This structure allows for powerful queries like, "Find all patients who take a medication that treats a condition that may be indicated by the symptom 'chest pain'."