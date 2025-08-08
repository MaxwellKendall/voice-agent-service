# MCP Server Scripts

This directory contains example scripts showing how to connect OpenAI to the MCP server.

## Quick Start

### 1. Set up environment variables

Create a `.env` file in the `services/mcp/` directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8000  # or your ngrok URL
```

### 2. Start the MCP server

```bash
cd services/mcp
python server.py
```

### 3. Run the example script

```bash
cd services/mcp/scripts
python simple_example.py
```

## Scripts

### `simple_example.py`

A minimal example showing the exact OpenAI MCP integration pattern:

```python
resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_label": "recipe-agent",
            "server_url": mcp_server_url,
            "require_approval": "never",
        },
    ],
    input="Can you search for some chicken pasta recipes?",
)
```

### `test_mcp_openai.py`

A comprehensive test script that demonstrates:

- Basic MCP connection
- Recipe search functionality
- Similar recipe finding
- Recipe extraction from URLs

## Usage with ngrok

If you want to expose your MCP server publicly:

```bash
# Install ngrok
# https://ngrok.com/download

# Start MCP server
cd services/mcp
python server.py

# In another terminal, expose with ngrok
ngrok http 8000

# Update your .env file with the ngrok URL
MCP_SERVER_URL=https://abc123.ngrok.io
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `MCP_SERVER_URL`: URL of your MCP server (default: http://localhost:8000)

## Troubleshooting

1. **Import Error**: Make sure you're running from the correct directory
2. **Connection Error**: Ensure the MCP server is running
3. **API Key Error**: Check your `OPENAI_API_KEY` environment variable
4. **ngrok Issues**: Verify the ngrok URL is accessible and update `MCP_SERVER_URL` 