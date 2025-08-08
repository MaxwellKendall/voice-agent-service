#!/usr/bin/env python3
"""
Simple example showing the exact OpenAI MCP integration pattern.

This demonstrates the exact code pattern you requested:
```python
resp = client.responses.create(
    model="gpt-4.1",
    tools=[
        {
            "type": "mcp",
            "server_label": "deepwiki",
            "server_url": "https://mcp.deepwiki.com/mcp",
            "require_approval": "never",
        },
    ],
    input="What transport protocols are supported in the 2025-03-26 version of the MCP spec?",
)
```
"""

import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Simple example of OpenAI MCP integration."""
    
    # Initialize OpenAI client
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1"
    )
    
    # Get MCP server URL from environment or use default
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    
    print(f"🔗 Using MCP server: {mcp_server_url}")
    print()
    
    try:
        # This is the exact pattern you requested
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
        
        print("✅ Success!")
        print("📝 Response:")
        print(resp.content[0].text)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("🔧 Make sure:")
        print("1. MCP server is running: python server.py")
        print("2. OPENAI_API_KEY is set in your environment")
        print("3. MCP_SERVER_URL points to your server (or use localhost:8000)")

if __name__ == "__main__":
    main() 