# Recipe Agent MCP Server

A standalone Model Context Protocol (MCP) server for recipe search and management with vector similarity capabilities.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
python server.py
```

The server will start on `http://localhost:8000`

### 4. Expose with ngrok (Optional)

```bash
# Install ngrok if you haven't already
# https://ngrok.com/download

# Expose the server
ngrok http 8000
```

You'll get a public URL like: `https://abc123.ngrok.io`

## 📋 Configuration

### Environment Variables

Create a `.env` file in the `services/mcp/` directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Database Configuration (Cloud URLs)
MONGODB_URL=mongodb+srv://username:password@your-cluster.mongodb.net/recipe_agent
QDRANT_URL=https://your-qdrant-instance.cloud

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# MCP Configuration
MCP_PROTOCOL_VERSION=2024-11-05
MCP_SERVER_NAME=Recipe Agent MCP Server
MCP_SERVER_VERSION=1.0.0

# Logging Configuration
LOG_LEVEL=INFO
```

### Database Setup

#### MongoDB (Cloud)
1. Create a MongoDB Atlas cluster
2. Get your connection string
3. Update `MONGODB_URL` in `.env`

#### Qdrant (Cloud)
1. Create a Qdrant Cloud instance
2. Get your API endpoint
3. Update `QDRANT_URL` in `.env`

## 🔧 Available Tools

The MCP server provides 4 recipe tools:

### 1. `search_recipes`
Search for recipes using natural language queries with vector similarity.

**Input**: `{"query": "chicken pasta recipes"}`

### 2. `get_similar_recipes`
Find recipes similar to a specific recipe using vector similarity.

**Input**: `{"recipe_id": "recipe-uuid-here"}`

### 3. `find_similar_recipes_from_url`
Find recipes similar to a recipe from a web URL using vector similarity.

**Input**: `{"recipe_url": "https://example.com/recipe"}`

### 4. `extract_and_store_recipe`
Extract recipe content from a URL, enrich with AI, and store in databases.

**Input**: `{"url": "https://example.com/recipe"}`

## 🌐 API Endpoints

### MCP Protocol
- `POST /` - Main MCP JSON-RPC endpoint

### Health & Info
- `GET /health` - Health check
- `GET /tools` - List available tools

## 🧪 Testing

### Test the Server

```bash
# Health check
curl http://localhost:8000/health

# List tools
curl http://localhost:8000/tools
```

### Test MCP Protocol

```bash
# Initialize connection
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "initialize",
    "params": {}
  }'

# List tools
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/list",
    "params": {}
  }'

# Search recipes
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "search_recipes",
      "arguments": {
        "query": "chicken pasta"
      }
    }
  }'
```

## 🔗 Integration with LLMs

### OpenAI Integration
The server can be connected to any LLM that supports MCP:

```python
# Example: Connect to OpenAI with MCP
import openai

client = openai.OpenAI(
    api_key="your_openai_key",
    base_url="https://api.openai.com/v1"
)

# Use the MCP server URL
mcp_server_url = "https://your-ngrok-url.ngrok.io"

# The LLM will automatically discover and use the MCP tools
```

### Claude Integration
```python
import anthropic

client = anthropic.Anthropic(
    api_key="your_anthropic_key"
)

# Claude will use the MCP server for tool calling
```

## 🏗️ Architecture

```
MCP Server
├── Direct MongoDB Connection (Storage)
├── Direct Qdrant Connection (Vector Search)
├── OpenAI Embeddings
└── Recipe Tools (4 tools)
```

### Database Operations
- **MongoDB**: Recipe storage, metadata, retrieval
- **Qdrant**: Vector similarity search, embeddings storage
- **OpenAI**: Text embeddings for similarity search

## 🚀 Deployment

### Local Development
```bash
cd services/mcp
python server.py
```

### Production with Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "server.py"]
```

### Cloud Deployment
1. Deploy to your preferred cloud platform
2. Set environment variables
3. Expose port 8000
4. Use ngrok or similar for public access

## 🔍 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
The server logs to stdout with configurable levels:
- `ERROR`: Errors only
- `WARN`: Warnings and errors
- `INFO`: General information (default)
- `DEBUG`: Detailed debugging

## 🛠️ Development

### Project Structure
```
services/mcp/
├── server.py          # FastAPI MCP server
├── database.py        # MongoDB + Qdrant operations
├── tools.py           # Recipe tool implementations
├── embeddings.py      # OpenAI embeddings
├── config.py          # Configuration management
├── requirements.txt   # Dependencies
├── env.example        # Environment template
└── README.md         # This file
```

### Adding New Tools
1. Add tool function to `tools.py`
2. Add tool definition to `server.py` in `get_tools()`
3. Add tool handler in `_handle_tools_call()`

### Testing
```bash
# Run architecture test
cd services
python test_architecture_simple.py
```

## 🔐 Security

### Environment Variables
- Never commit `.env` files
- Use secure cloud databases
- Rotate API keys regularly

### Network Security
- Use HTTPS in production
- Implement authentication if needed
- Monitor access logs

## 📞 Support

### Common Issues

1. **Configuration Error**: Check your `.env` file
2. **Database Connection**: Verify MongoDB and Qdrant URLs
3. **OpenAI API**: Ensure API key is valid
4. **ngrok Issues**: Check ngrok status and URL

### Debug Mode
Set `DEBUG=true` in your `.env` file for detailed logging.

## 📄 License

This project is part of the Recipe Agent system. 