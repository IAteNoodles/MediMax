# MediMax Backend - Abhishek

This directory, `backend_abhishek`, contains the primary backend API for the MediMax application. It is a comprehensive FastAPI service responsible for a wide range of functionalities, including patient data management, interaction with a Neo4j graph database, and communication with an external "agentic" system for advanced AI analysis.

## Tech Stack

- **Web Framework**: `FastAPI`
- **Databases**:
  - **Primary/Relational**: `MariaDB` / `MySQL` (via `pymysql`) for storing structured patient data.
  - **Graph**: `Neo4j` (via `neo4j`) for knowledge graph operations.
- **AI/LLM Integration**:
  - `Ollama` with the `MedGemma` model for generating AI-powered medical summaries.
  - `httpx` for making asynchronous requests to an external agentic server.
- **Configuration**: `python-dotenv` for managing environment variables.
- **Data Validation**: `Pydantic` for request and response data modeling.
- **Frontend (for testing)**: A `Streamlit` application (`streamlit_app.py`) is included to provide a simple UI for testing the API endpoints.

---

## Core Functionality

The main application is a single, large FastAPI file: `app.py`. It serves as the central hub for all backend logic.

### What This Module Essentially Does:

This backend acts as a **Medical Data and AI Orchestration Layer**. Its primary responsibilities are:

1.  **CRUD Operations for Patient Data**: It provides a rich set of API endpoints to Create, Read, Update, and Delete patient records and their associated medical data (medical history, appointments, medications, lab reports, etc.) in a relational database.

2.  **Knowledge Graph Interaction**: It can connect to a Neo4j database to execute complex Cypher queries. This allows for advanced analysis and retrieval of interconnected medical data that is not easily represented in a relational model.

3.  **AI-Powered Summarization**: It integrates with a local Ollama instance running the `MedGemma` model. The `/get_medical_history/{patient_id}` endpoint can fetch a patient's history and use the LLM to generate a concise, medically relevant summary.

4.  **Agentic System Bridge**: It acts as a bridge to an external, more advanced AI "agentic" system. It can forward complex assessment requests to this system and retrieve the results. It also includes an endpoint (`/frontend/get_query`) that automatically aggregates a patient's data from the database to formulate a comprehensive query for this agentic system.

5.  **Health and API Discovery**: It includes endpoints for health checks (`/health`) and for listing all available API endpoints (`/api/endpoints`), making the API self-documenting and easy to monitor.

---

## Key Components

### `app.py`

This is the monolithic FastAPI application containing all the logic.

- **Database Connections**:
  - `get_db_connection()`: A dependency that provides a connection to the MariaDB/MySQL database.
  - `get_neo4j_driver()`: A function to create and configure a robust driver for connecting to the Neo4j Aura database, complete with retry logic and connection pooling.

- **Patient Management Endpoints**:
  - `GET /db/get_all_patients`: Retrieves a paginated list of all patients.
  - `GET /db/get_complete_patient_profile/{patient_id}`: A powerful endpoint that fetches a patient's entire medical record, including history, medications, appointments, and lab reports, from the database and compiles it into a single JSON object.
  - `POST /db/new_patient`, `PUT /db/update_patient/{patient_id}`, `DELETE /db/delete_patient/{patient_id}`: Standard CRUD operations for patients.

- **Medical Record Endpoints**:
  - `POST /db/add_medical_history/{patient_id}`: Adds a new medical history item.
  - `POST /db/add_appointment/{patient_id}`: Schedules a new appointment.
  - `POST /db/add_medication/{patient_id}`: Adds a new medication record.
  - `POST /db/add_lab_report/{patient_id}`: Creates a new lab report.

- **AI and Agentic Endpoints**:
  - `GET /get_medical_history/{patient_id}`: Fetches medical history and generates an AI summary.
  - `POST /assess`: Forwards a detailed patient assessment request to the external agentic server.
  - `GET /frontend/get_query`: Automatically generates a patient summary text to be used in an assessment query.

### `streamlit_app.py`

A simple web-based user interface built with Streamlit. This app is designed for **testing and demonstration purposes**. It provides forms and buttons to easily interact with the main FastAPI endpoints without needing to use `curl` or another API client.

### `mock.py` and `mock_data.json`

- `mock.py`: A Python script that acts as a mock client. It sends predefined requests to the FastAPI server to test its endpoints.
- `mock_data.json`: Contains sample patient data used by the mock client and the `/assess_mock` endpoint for testing.

---

## Setup and How to Run

1.  **Environment Variables**: Create a `.env` file in the parent directory (`MediMax/`) and populate it with the necessary database and service credentials:
    ```
    # MariaDB/MySQL
    DB_HOST=your_host
    DB_PORT=3306
    DB_NAME=your_db_name
    DB_USER=your_user
    DB_PASSWORD=your_password

    # Neo4j Aura
    NEO4J_URI=your_neo4j_uri
    AURA_USER=neo4j
    AURA_PASSWORD=your_aura_password

    # Agentic Server
    AGENTIC_ADDRESS=http://address_of_agentic_server
    ```

2.  **Install Dependencies**: The required dependencies are listed in the main `requirements.txt` in the parent directory (`MediMax/`). Ensure they are installed in your Python environment.
    ```bash
    # From the MediMax/ directory
    pip install -r requirements.txt
    ```
    You may also need to install `ollama` if it's not already listed:
    ```bash
    pip install ollama
    ```

3.  **Run the Main Backend API**:
    ```bash
    # Navigate to the backend_abhishek directory
    cd backend_abhishek

    # Run the FastAPI application
    python app.py
    ```
    The server will start on `http://127.0.0.1:8821`.

4.  **(Optional) Run the Streamlit Test App**: To use the UI for testing, run the Streamlit app in a separate terminal.
    ```bash
    # Navigate to the backend_abhishek directory
    cd backend_abhishek

    # Run the Streamlit app
    streamlit run streamlit_app.py
    ```
    This will open a new tab in your browser with the test interface.