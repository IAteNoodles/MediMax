# Docker Setup for Backend Noodles

This directory contains Docker configurations for containerizing the backend services with separate Dockerfiles for each service.

## Files Created

- `backend_noodles/Dockerfile.chat_api`: Dockerfile for the chat API service
- `backend_noodles/Dockerfile.mcp_server`: Dockerfile for the MCP server service
- `docker-compose.backend.yml`: Docker Compose configuration for both services

## Key Features

- **Separate Dockerfiles**: Each service has its own Dockerfile in the `backend_noodles` directory
- **Configurable API URL**: The chat API can connect to different MCP server URLs via environment variable
- **Security**: Non-root user execution
- **Health checks**: Built-in health monitoring for both services
- **Environment variables**: Support for `.env` file configuration

## Environment Variables

### Required in `.env` file:
- `GOOGLE_API_KEY`: Your Google Generative AI API key

### Optional for Chat API:
- `MCP_SERVER_URL`: URL of the MCP server (default: `http://mcp-server:8005/mcp/` for Docker, `http://127.0.0.1:8005/mcp/` for local)

## Building and Running

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and run both services
docker-compose -f docker-compose.backend.yml up --build

# Run in background
docker-compose -f docker-compose.backend.yml up -d --build

# Stop services
docker-compose -f docker-compose.backend.yml down
```

### Option 2: Building Individual Images

#### Build MCP Server
```bash
cd backend_noodles
docker build -f Dockerfile.mcp_server -t medimax-mcp-server .
```

#### Build Chat API
```bash
cd backend_noodles
docker build -f Dockerfile.chat_api -t medimax-chat-api .
```

#### Run the containers
```bash
# Run MCP Server
docker run -p 8005:8005 --env-file ../.env --name mcp-server medimax-mcp-server

# Run Chat API (in another terminal)
docker run -p 8000:8000 --env-file ../.env -e MCP_SERVER_URL=http://127.0.0.1:8005/mcp/ --name chat-api medimax-chat-api
```

## Customizing API URL

### For Docker Compose:
Edit the `docker-compose.backend.yml` file:
```yaml
chat-api:
  environment:
    - MCP_SERVER_URL=http://your-custom-mcp-server:8005/mcp/
```

### For Individual Containers:
```bash
docker run -p 8000:8000 --env-file .env -e MCP_SERVER_URL=http://your-server:8005/mcp/ medimax-chat-api
```

### For Local Development:
Set the environment variable before running:
```bash
export MCP_SERVER_URL=http://127.0.0.1:8005/mcp/
python chat_api.py
```

## Ports

- Chat API: 8000
- MCP Server: 8005

## Health Checks

Both services include health checks that verify the services are responding correctly:
- Chat API: Checks `/docs` endpoint
- MCP Server: Checks `/mcp/` endpoint

## Troubleshooting

- **Connection Issues**: Ensure the MCP server is running before starting the chat API
- **Environment Variables**: Verify your `.env` file contains the required variables
- **Port Conflicts**: Make sure ports 8000 and 8005 are available
- **Network Issues**: When using Docker, services communicate via the `medimax-network`