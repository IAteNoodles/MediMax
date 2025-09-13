# Chat API with LangChain and Google GenAI

This is a FastAPI-based chat API that integrates with Google GenAI model and connects to an MCP server for additional tools.

## Setup

1. Ensure you have Python installed.
2. Install dependencies:
   ```
   pip install langchain langchain_mcp_adapters langchain_google_genai google-generativeai python-dotenv fastapi uvicorn
   ```

3. Set up your Google API key:
   - Create a `.env` file in the project root with:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     mcp_config_path=.vscode\mcp.json
     ```
   - Replace `your_google_api_key_here` with your actual Google API key.

4. Ensure the MCP server is running. Run the MCP server first:
   ```
   cd backend_noodles
   python mcp_server.py
   ```

## Running the API

1. Navigate to the backend_noodles directory:
   ```
   cd backend_noodles
   ```

2. Run the API:
   ```
   python chat_api.py
   ```

   This will start the server on `http://0.0.0.0:8000`

## Usage

Send a POST request to `/chat` with JSON:
```json
{
  "message": "Hello, how are you?"
}
```

Response:
```json
{
  "response": "AI response here"
}
```

## Exposing to Internet

To expose the API to the internet:

- If running on a server with public IP, ensure port 8000 is open.
- For local development, use a tunneling service like ngrok:
  ```
  npx ngrok http 8000
  ```
  This will give you a public URL.

## Troubleshooting

- Ensure MCP server is running on port 8005.
- Check that `.env` file is in the project root.
- Verify Google API key is set.
- If CORS issues, the API allows all origins.