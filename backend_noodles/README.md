# Backend Noodles

This folder contains the backend components for the MediMax application, providing a conversational AI interface integrated with medical prediction tools via the Model Context Protocol (MCP).

## Components

### `chat_api.py`
A FastAPI-based chat API that leverages LangChain and Google Generative AI (Gemini 1.5 Flash) to create an intelligent conversational agent. The agent can utilize tools provided by the MCP server to perform medical risk predictions.

**Key Features:**
- Asynchronous processing with FastAPI
- Integration with MCP tools for cardiovascular and diabetes risk assessment
- Conversation memory using LangChain's ConversationBufferMemory
- CORS enabled for cross-origin requests
- Runs on port 8000 by default

### `mcp_server.py`
An MCP server built with FastMCP that exposes tools for medical predictions. It acts as a bridge between the chat API and the local AI model services for cardiovascular and diabetes risk prediction.

**Exposed Tools:**
- `Hello`: A simple greeting function
- `Predict_Cardiovascular_Risk_With_Explanation`: Predicts cardiovascular risk based on patient data
- `Predict_Diabetes_Risk_With_Explanation`: Predicts diabetes risk based on patient data

The server runs on port 8005 using streamable HTTP transport.

## Dependencies

Install the required Python packages:

```
pip install langchain langchain_mcp_adapters langchain_google_genai google-generativeai python-dotenv fastapi uvicorn requests fastmcp
```

## Setup

1. Ensure you have Python 3.8+ installed.

2. Set up environment variables:
   - Create a `.env` file in the project root with:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     ```

3. Ensure the AI model services are running:
   - Cardiovascular prediction service on `http://localhost:5002`
   - Diabetes prediction service on `http://localhost:5003`

## Running

1. Start the MCP server:
   ```
   python mcp_server.py
   ```

2. In a separate terminal, start the chat API:
   ```
   python chat_api.py
   ```

The chat API will be available at `http://127.0.0.1:8000` and `http://0.0.0.0:8000`.

## API Endpoints

### Chat API (`chat_api.py`)

#### POST `/chat`
Processes a user message through the LangChain agent and returns a conversational response.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "message": "string"  // The user's message to process
  }
  ```

**Response:**
- Status: `200 OK` on success, `500 Internal Server Error` on failure
- Content-Type: `application/json`
- Body:
  ```json
  {
    "response": "string"  // The agent's response, which may include tool outputs
  }
  ```

**Example:**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, can you predict cardiovascular risk for a 45-year-old male?"}'
```

**Error Response:**
```json
{
  "detail": "string"  // Error message if agent is not initialized or processing fails
}
```

## MCP Tools (`mcp_server.py`)

The MCP server exposes the following tools that can be invoked by the LangChain agent in the chat API.

### Tool: `Hello`
A simple greeting function for testing purposes.

**Input Parameters:**
- `name` (str): The name to greet

**Output:**
- `str`: A greeting message in the format "Hello, Bro {name}!"

**Example Usage:**
- Input: `name="Alice"`
- Output: `"Hello, Bro Alice!"`

### Tool: `Predict_Cardiovascular_Risk_With_Explanation`
Predicts cardiovascular risk based on patient health data and returns the prediction with explanation.

**Input Parameters:**
- `age` (float): Age in years
- `gender` (int): 1 = Female, 2 = Male
- `height` (float): Height in centimeters
- `weight` (float): Weight in kilograms
- `ap_hi` (int): Systolic blood pressure
- `ap_lo` (int): Diastolic blood pressure
- `cholesterol` (int): 1 = Normal, 2 = Above normal, 3 = Well above normal
- `gluc` (int): Glucose level (1 = Normal, 2 = Above normal, 3 = Well above normal)
- `smoke` (int): 0 = No, 1 = Yes
- `alco` (int): Alcohol consumption (0 = No, 1 = Yes)
- `active` (int): Physical activity (0 = No, 1 = Yes)

**Output:**
- `dict`: JSON response from the cardiovascular prediction service, typically containing:
  - `prediction`: The risk prediction (e.g., 0 or 1 for low/high risk)
  - `probability`: Probability score
  - `explanation`: Text explanation of the prediction
  - Additional fields depending on the service implementation

**Example Output:**
```json
{
  "prediction": 1,
  "probability": 0.85,
  "explanation": "High risk due to elevated cholesterol and blood pressure."
}
```

**Error Output:**
```json
{
  "error": "request_failed",
  "details": "Connection timeout or service unavailable"
}
```

### Tool: `Predict_Diabetes_Risk_With_Explanation`
Predicts diabetes risk based on patient health data and returns the prediction with explanation.

**Input Parameters:**
- `age` (float): Age in years
- `gender` (str): "Female", "Male", or "Other"
- `hypertension` (int): 0 = No, 1 = Yes
- `heart_disease` (int): 0 = No, 1 = Yes
- `smoking_history` (str): "never", "No Info", "current", "former", "ever", "not current"
- `bmi` (float): Body Mass Index
- `HbA1c_level` (float): Hemoglobin A1c level
- `blood_glucose_level` (float): Blood glucose level in mg/dL

**Output:**
- `dict`: JSON response from the diabetes prediction service, typically containing:
  - `prediction`: The risk prediction (e.g., 0 or 1 for low/high risk)
  - `probability`: Probability score
  - `explanation`: Text explanation of the prediction
  - Additional fields depending on the service implementation

**Example Output:**
```json
{
  "prediction": 1,
  "probability": 0.72,
  "explanation": "High risk due to elevated HbA1c and BMI."
}
```

**Error Output:**
```json
{
  "error": "request_failed",
  "details": "Connection timeout or service unavailable"
}
```

## Architecture

- The chat API initializes an MCP client to fetch tools from the MCP server.
- LangChain agent uses these tools to enhance its conversational capabilities.
- Medical predictions are delegated to specialized AI models running in separate services.
- All components communicate via HTTP APIs for modularity.

## Troubleshooting

- Ensure all required services are running and accessible on their respective ports.
- Verify the `.env` file contains the correct Google API key.
- Check network connectivity if services are running in containers or remote machines.
- Review console logs for detailed error messages.