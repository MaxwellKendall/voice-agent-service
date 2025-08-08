from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Prefer localhost:8000 while debugging; override with MCP_URL or ngrok
url = "https://6d14fe7fd8d1.ngrok-free.app"

resp = client.responses.create(
    model="gpt-4.1",
    tool_choice="required",  # force tool usage
    tools=[{
        "type": "mcp",
        "server_label": "dice_server",
        "server_url": f"{url}/mcp/",
        "require_approval": "never",
    }],
    input="Roll 3 dice",
)
print(resp.output_text)