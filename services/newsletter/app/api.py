"""FastAPI application with chat endpoint."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from app.models import ChatRequest, ChatResponse, HealthResponse, ChatListResponse, ChatInfo
from app.agent import process_query
from app.mongo import get_chat_service

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
    
    If chat_id is null, a new chat session will be created.
    """
    try:
        logger.info(f"Received chat request: {request.message[:100]}...")
        
        chat_service = get_chat_service()
        
        # Handle chat ID - create new chat if none provided
        if request.chat_id is None:
            # Create a new chat
            chat_id = await chat_service.create_chat()
            logger.info(f"Created new chat with ID: {chat_id}")
        else:
            # Verify existing chat exists
            chat = await chat_service.get_chat(request.chat_id)
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")
            chat_id = request.chat_id
            logger.info(f"Using existing chat: {chat_id}")
        
        # Get chat history for the agent
        chat_history = await chat_service.get_chat_history_for_agent(chat_id)
        
        # Process the query through the AI agent
        response = process_query(
            query=request.message,
            chat_history=chat_history
        )
        
        # Save the user message
        await chat_service.add_message(chat_id, "user", request.message)
        
        # Save the assistant response
        await chat_service.add_message(chat_id, "assistant", response)
        
        logger.info("Chat request processed successfully")
        
        return ChatResponse(
            response=response,
            chat_id=chat_id,
            recipes=None,  # Could be enhanced to extract recipes from response
            tool_calls=None  # Could be enhanced to track tool usage
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/chats", response_model=ChatListResponse)
async def get_chats():
    """
    Get all chat sessions.
    
    Returns a list of all chat sessions with their metadata.
    """
    try:
        logger.info("Retrieving all chats")
        
        chat_service = get_chat_service()
        chats = await chat_service.get_all_chats()
        
        # Convert to response format
        chat_list = []
        for chat in chats:
            chat_list.append(ChatInfo(
                id=chat["_id"],
                title=chat["title"],
                created_at=chat["created_at"],
                updated_at=chat["updated_at"],
                message_count=chat["message_count"]
            ))
        
        logger.info(f"Retrieved {len(chat_list)} chats")
        
        return ChatListResponse(chats=chat_list)
        
    except Exception as e:
        logger.error(f"Error retrieving chats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/chats/{chat_id}")
async def get_chat(chat_id: str):
    """
    Get a specific chat with all its messages.
    
    Args:
        chat_id: The chat ID
        
    Returns:
        Chat information with all messages
    """
    try:
        logger.info(f"Retrieving chat: {chat_id}")
        
        chat_service = get_chat_service()
        
        # Get chat info
        chat = await chat_service.get_chat(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Get chat messages
        messages = await chat_service.get_chat_messages(chat_id)
        
        return {
            "chat": {
                "id": chat["_id"],
                "title": chat["title"],
                "created_at": chat["created_at"],
                "updated_at": chat["updated_at"],
                "message_count": chat["message_count"]
            },
            "messages": messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat {chat_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """
    Delete a chat and all its messages.
    
    Args:
        chat_id: The chat ID
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Deleting chat: {chat_id}")
        
        chat_service = get_chat_service()
        success = await chat_service.delete_chat(chat_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        return {"message": "Chat deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat {chat_id}: {e}")
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