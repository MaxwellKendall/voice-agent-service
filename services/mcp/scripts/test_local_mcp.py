#!/usr/bin/env python3
"""
Test OpenAI MCP integration with local server.
"""

import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    
    # Use ngrok URL that forwards to localhost:8000/mcp
    mcp_server_url = "https://ee46ffb98a27.ngrok-free.app/mcp/"
    print(f"🔗 Using MCP server via ngrok: {mcp_server_url}")
    
    try:
        resp = client.responses.create(
            model="gpt-4.1",
            tools=[
                {
                    "type": "mcp",
                    "server_label": "recipe-agent",  # match the server name
                    "server_url": mcp_server_url,
                    "require_approval": "never",
                },
            ],
            input="Give me a good recipe for a friday night dinner for a family of 4."
        )
        
        print("✅ Success!")
        print("📝 Response:")
        print(resp.output_text)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔧 Make sure:")
        print("1. MCP server is running locally: python server.py")
        print("2. OPENAI_API_KEY is set in your environment")
        print("3. The ngrok tunnel is active and forwarding to localhost:8000")

if __name__ == "__main__":
    main() 