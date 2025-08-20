#!/usr/bin/env python3
"""
Test script for the Cooking Assistant WebSocket Server.
"""

import asyncio
import json
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_RECIPE_ID = "681d67ee72c0a5030e4b2875" # fluffy pancakes

async def test_websocket_connection():
    """Test the WebSocket connection to the cooking assistant server."""
    
    # Test client ID
    client_id = "test_client_123"
    
    # WebSocket URL
    uri = f"ws://localhost:8001/ws/cooking-assistant/{client_id}"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            
            # Test 1: Send a text message
            test_message = {
                "type": "text",
                "content": "Is it possible to make this dairy free?",
                "recipe_id": TEST_RECIPE_ID
            }
            
            logger.info(f"Sending test message: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Wait for response
            response = await websocket.recv()
            response_data = json.loads(response)
            
            logger.info(f"Received response: {response_data}")
            
            # Test 2: Send an audio transcription
            test_audio_message = {
                "type": "audio_transcription",
                "content": "Is it possible to make this dairy free?",
                "recipe_id": TEST_RECIPE_ID
            }
            
            logger.info(f"Sending audio transcription: {test_audio_message}")
            await websocket.send(json.dumps(test_audio_message))
            
            # Wait for response
            response2 = await websocket.recv()
            response_data2 = json.loads(response2)
            
            logger.info(f"Received response: {response_data2}")
            
            # Test 3: Send a recipe search request
            search_message = {
                "type": "text",
                "content": "Find me some vegetarian pasta recipes",
                "recipe_id": None
            }
            
            logger.info(f"Sending search request: {search_message}")
            await websocket.send(json.dumps(search_message))
            
            # Wait for response
            response3 = await websocket.recv()
            response_data3 = json.loads(response3)
            
            logger.info(f"Received response: {response_data3}")
            
    except Exception as e:
        logger.error(f"Error during test: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())
