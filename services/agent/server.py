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
import base64
import tempfile
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

async def generate_tts_audio(text: str) -> Optional[str]:
    """Generate TTS audio from text using OpenAI TTS API."""
    try:
        logger.info(f"Generating TTS audio for text: {text[:100]}...")
        
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Generate audio using OpenAI TTS
        response = client.audio.speech.create(
            model="tts-1",  # OpenAI's TTS model
            voice="alloy",  # You can choose: alloy, echo, fable, onyx, nova, shimmer
            input=text
        )
        
        # Save the audio to the temporary file
        with open(temp_path, "wb") as audio_file:
            for chunk in response.iter_bytes():
                audio_file.write(chunk)
        
        # Read the audio file and convert to base64
        with open(temp_path, "rb") as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        logger.info(f"TTS audio generated successfully, size: {len(audio_data)} bytes")
        return audio_base64
        
    except Exception as e:
        logger.error(f"Error generating TTS audio: {e}")
        logger.error(traceback.format_exc())
        return None

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
            "content": error_message
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
            "content": text
        })
        
        # Send typing indicator
        await manager.send_message(client_id, {"type": "typing", "status": "started"})
        
        # Get response from OpenAI with MCP integration
        response = await get_ai_response(client_id, text, recipe_id)
        
        # Add assistant response to conversation history
        manager.conversations[client_id].append({
            "role": "assistant", 
            "content": response
        })
        
        # Generate TTS audio for the response
        audio_base64 = await generate_tts_audio(response)
        
        # Send response with audio
        await manager.send_message(client_id, {
            "type": "response",
            "content": response,
            "audio": audio_base64
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
        system_message = f"""
You are a hands-free cooking assistant. Your role is to guide the user step-by-step through cooking a specific recipe.  

The recipe data for the session is located at: data://recipe/{recipe_id}  

Context: This is the active recipe we are working on. You should treat this recipe as the sole source of truth for ingredients, steps, and instructions.  

Goals:  
- Help the user understand and prepare the recipe one step at a time.  
- Be conversational and adaptive (e.g., repeat, clarify, or simplify instructions when asked).  
- Track progress through the recipe, remembering which step the user is on.  
- Offer practical cooking tips (timing cues, substitutions, safety reminders) where useful.  
- Only reference the current recipe; do not suggest unrelated recipes unless explicitly asked.  

You may access the recipe data via the MCP resource provided. Always ground your guidance in that data. 
        """
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
                "extract_and_store_recipe",
                "get_recipe_by_id"
            ],
        }]
        
        # Make API call with timeout
        try:
            resp = await asyncio.wait_for(
                asyncio.to_thread(
                    client.responses.create,
                    model=OPENAI_MODEL,
                    tools=tools,
                    input=conversation,
                    instructions=system_message
                ),
                timeout=30.0
            )
            
            if resp.output_text:
                return resp.output_text
            else:
                return "I'm sorry, I couldn't generate a response. Please try again."

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
