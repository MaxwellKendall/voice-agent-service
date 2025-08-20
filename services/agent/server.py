#!/usr/bin/env python3
"""
Cooking Assistant Agent Server using FastAPI and WebSockets.
Connects to MCP server using OpenAI's MCP integration.
"""

import os
import json
import logging
import asyncio
import traceback
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# FastAPI and WebSocket imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# OpenAI imports
from openai import OpenAI
from openai import APIError, RateLimitError, APITimeoutError, APIConnectionError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://ee46ffb98a27.ngrok-free.app/mcp") # should be some ngrok url!

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Initialize OpenAI client
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    raise

# Initialize FastAPI app
app = FastAPI(title="Cooking Assistant Agent Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    """Manages WebSocket connections and conversation history."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.conversations: Dict[str, list] = {}
        self.logger = logging.getLogger(__name__)
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new client and initialize conversation."""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            if client_id not in self.conversations:
                self.conversations[client_id] = []
            self.logger.info(f"Client {client_id} connected successfully")
            
            # Send welcome message
            await self.send_message(client_id, {
                "type": "system",
                "content": "Connected to Cooking Assistant. I'm ready to help you cook!"
            })
            
        except Exception as e:
            self.logger.error(f"Failed to connect client {client_id}: {e}")
            raise
    
    def disconnect(self, client_id: str):
        """Disconnect a client and clean up resources."""
        try:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            if client_id in self.conversations:
                del self.conversations[client_id]
            self.logger.info(f"Client {client_id} disconnected")
        except Exception as e:
            self.logger.error(f"Error during disconnect for client {client_id}: {e}")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send a message to a specific client with error handling."""
        try:
            if client_id in self.active_connections:
                await self.active_connections[client_id].send_text(json.dumps(message))
            else:
                self.logger.warning(f"Attempted to send message to disconnected client {client_id}")
        except Exception as e:
            self.logger.error(f"Failed to send message to client {client_id}: {e}")
            # Mark connection as broken
            self.disconnect(client_id)
    
    async def send_error(self, client_id: str, error_message: str, error_type: str = "error"):
        """Send an error message to a client."""
        await self.send_message(client_id, {
            "type": error_type,
            "content": error_message,
            "timestamp": asyncio.get_event_loop().time()
        })

# Global connection manager
manager = ConnectionManager()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "active_connections": len(manager.active_connections),
            "mcp_server_url": MCP_SERVER_URL
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/status")
async def status_check():
    """Detailed status endpoint."""
    try:
        return {
            "status": "operational",
            "active_connections": len(manager.active_connections),
            "conversations": len(manager.conversations),
            "mcp_server_url": MCP_SERVER_URL,
            "openai_configured": bool(OPENAI_API_KEY)
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

@app.websocket("/ws/cooking-assistant/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for cooking assistant interactions."""
    
    # Validate client_id
    if not client_id or len(client_id) > 100:
        await websocket.close(code=1008, reason="Invalid client ID")
        return
    
    try:
        # Connect the client
        await manager.connect(websocket, client_id)
        logger.info(f"WebSocket connection established for client {client_id}")
        
        # Main message handling loop
        while True:
            try:
                # Receive message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Parse message
                try:
                    message = json.loads(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from client {client_id}: {e}")
                    await manager.send_error(client_id, "Invalid message format. Please send valid JSON.")
                    continue
                
                # Validate message structure
                if not isinstance(message, dict) or "type" not in message:
                    await manager.send_error(client_id, "Message must be a JSON object with a 'type' field.")
                    continue
                
                # Handle different message types
                await handle_message(client_id, message)
                
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_text(json.dumps({"type": "ping"}))
                except Exception as e:
                    logger.warning(f"Failed to send ping to client {client_id}: {e}")
                    break
                    
            except WebSocketDisconnect:
                logger.info(f"Client {client_id} disconnected normally")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error handling message from client {client_id}: {e}")
                logger.error(traceback.format_exc())
                await manager.send_error(client_id, "An unexpected error occurred. Please try again.")
                break
                
    except Exception as e:
        logger.error(f"Error in WebSocket connection for client {client_id}: {e}")
        logger.error(traceback.format_exc())
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
    finally:
        # Always clean up
        manager.disconnect(client_id)

async def handle_message(client_id: str, message: Dict[str, Any]):
    """Handle incoming messages from clients."""
    
    message_type = message.get("type")
    content = message.get("content", "")
    recipe_id = message.get("recipe_id")
    
    logger.info(f"Received {message_type} message from client {client_id}")
    
    try:
        if message_type == "text":
            await handle_text_message(client_id, content, recipe_id)
        elif message_type == "audio_transcription":
            await handle_audio_message(client_id, content, recipe_id)
        elif message_type == "ping":
            await manager.send_message(client_id, {"type": "pong"})
        else:
            await manager.send_error(client_id, f"Unknown message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling {message_type} message from client {client_id}: {e}")
        logger.error(traceback.format_exc())
        await manager.send_error(client_id, f"Failed to process {message_type} message")

async def handle_text_message(client_id: str, text: str, recipe_id: Optional[str] = None):
    """Handle text messages from clients."""
    
    if not text.strip():
        await manager.send_error(client_id, "Message cannot be empty")
        return
    
    try:
        # Add user message to conversation history
        manager.conversations[client_id].append({
            "role": "user",
            "content": text,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Send typing indicator
        await manager.send_message(client_id, {"type": "typing", "status": "started"})
        
        # Get response from OpenAI with MCP integration
        response = await get_ai_response(client_id, text, recipe_id)
        
        # Add assistant response to conversation history
        manager.conversations[client_id].append({
            "role": "assistant", 
            "content": response,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Send response
        await manager.send_message(client_id, {
            "type": "response",
            "content": response
        })
        
    except Exception as e:
        logger.error(f"Error handling text message from client {client_id}: {e}")
        await manager.send_error(client_id, "Failed to process your message. Please try again.")

async def handle_audio_message(client_id: str, transcription: str, recipe_id: Optional[str] = None):
    """Handle audio transcription messages from clients."""
    
    if not transcription.strip():
        await manager.send_error(client_id, "Audio transcription cannot be empty")
        return
    
    # Treat audio transcription the same as text
    await handle_text_message(client_id, transcription, recipe_id)

async def get_ai_response(client_id: str, user_message: str, recipe_id: Optional[str] = None) -> str:
    """Get response from OpenAI with MCP integration and comprehensive error handling."""
    
    try:
        # Prepare conversation context
        conversation = manager.conversations[client_id]
        
        # Build system message with recipe context
        system_message = "You are a highly specialized expert in cooking. Your job is to help the user cook a specific recipe. Anticipate direct questions and answer them directly and concisely." 
        if recipe_id:
            system_message += f" The user is currently cooking recipe ID: {recipe_id}. Use the resource at data://recipe/{recipe_id} to get the recipe details."
        
        # Prepare tools configuration
        tools = [{
            "type": "mcp",
            "server_label": "recipe-agent",
            "server_url": MCP_SERVER_URL,
            "require_approval": "never",
            "allowed_tools": [
                "search_recipes", 
                "get_similar_recipes",
                "find_similar_recipes_from_url",
                "extract_and_store_recipe"
            ],
        }]
        
        # Make API call with timeout
        try:
            resp = await asyncio.wait_for(
                asyncio.to_thread(
                    client.responses.create,
                    model=OPENAI_MODEL,
                    tools=tools,
                    input=conversation + user_message,
                    instructions=system_message
                ),
                timeout=30.0
            )
            
            if resp.output_text:
                return resp.output_text
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."
                
        except asyncio.TimeoutError:
            logger.error(f"OpenAI API timeout for client {client_id}")
            return "I'm taking longer than expected to respond. Please try again."
            
        except RateLimitError:
            logger.error(f"OpenAI rate limit exceeded for client {client_id}")
            return "I'm receiving too many requests right now. Please wait a moment and try again."
            
        except APITimeoutError:
            logger.error(f"OpenAI API timeout for client {client_id}")
            return "The service is taking longer than expected. Please try again."
            
        except APIConnectionError:
            logger.error(f"OpenAI API connection error for client {client_id}")
            return "I'm having trouble connecting to my services. Please check your internet connection and try again."
            
        except APIError as e:
            logger.error(f"OpenAI API error for client {client_id}: {e}")
            return "I'm experiencing technical difficulties. Please try again later."
            
        except Exception as e:
            logger.error(f"Unexpected error calling OpenAI API for client {client_id}: {e}")
            logger.error(traceback.format_exc())
            return "An unexpected error occurred. Please try again."
            
    except Exception as e:
        logger.error(f"Error in get_ai_response for client {client_id}: {e}")
        logger.error(traceback.format_exc())
        return "I'm having trouble processing your request. Please try again."

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Log startup information
    logger.info("Starting Cooking Assistant Agent Server...")
    logger.info(f"MCP Server URL: {MCP_SERVER_URL}")
    logger.info(f"OpenAI API Key configured: {bool(OPENAI_API_KEY)}")
    
    try:
        uvicorn.run(
            "server:app",
            host="0.0.0.0",
            port=8001,
            reload=False,  # Disable reload in production
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.error(traceback.format_exc())
        raise
