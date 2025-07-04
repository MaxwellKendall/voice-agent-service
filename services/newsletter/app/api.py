"""FastAPI application with chat endpoint."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from app.models import ChatRequest, ChatResponse, HealthResponse
from app.agent import process_query

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Recipe Agent API",
    description="An AI agent that helps with recipe recommendations and cooking advice, building toward newsletter generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message through the AI agent.
    
    This endpoint accepts natural language queries and returns the AI agent's response.
    The agent can search for recipes, find similar recipes, and provide cooking advice.
    The entire conversation is designed to build content for a newsletter.
    """
    try:
        logger.info(f"Received chat request: {request.message[:100]}...")
        
        # Process the query through the AI agent
        response = process_query(
            query=request.message,
            chat_history=request.chat_history
        )
        
        logger.info("Chat request processed successfully")
        
        return ChatResponse(
            response=response,
            recipes=None,  # Could be enhanced to extract recipes from response
            tool_calls=None  # Could be enhanced to track tool usage
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/tools")
async def list_tools():
    """List available tools for the AI agent."""
    from app.tools import get_available_tools
    
    tools = get_available_tools()
    tool_info = []
    
    for tool in tools:
        tool_info.append({
            "name": tool.name,
            "description": tool.description,
            "args_schema": str(tool.args_schema) if hasattr(tool, 'args_schema') else None
        })
    
    return {"tools": tool_info} 