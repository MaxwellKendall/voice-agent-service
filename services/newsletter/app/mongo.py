"""MongoDB database operations for chat persistence."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId

from app.config import get_mongodb_uri, get_mongodb_database

logger = logging.getLogger(__name__)

# Global database client and database instances
_client: AsyncIOMotorClient = None
_database: AsyncIOMotorDatabase = None

def get_database() -> AsyncIOMotorDatabase:
    """Get the MongoDB database instance."""
    global _database
    if _database is None:
        global _client
        if _client is None:
            uri = get_mongodb_uri()
            _client = AsyncIOMotorClient(uri)
            logger.info("MongoDB client initialized")
        
        database_name = get_mongodb_database()
        _database = _client[database_name]
        logger.info(f"Using MongoDB database: {database_name}")
    
    return _database

async def close_database():
    """Close the MongoDB connection."""
    global _client, _database
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("MongoDB connection closed")

class ChatService:
    """Service for managing chat operations in MongoDB."""
    
    def __init__(self):
        self.db = get_database()
        self.chats_collection = self.db.chats
        self.messages_collection = self.db.messages
    
    async def create_chat(self, title: str = None) -> str:
        """
        Create a new chat session.
        
        Args:
            title: Optional title for the chat
            
        Returns:
            The chat ID as a string
        """
        try:
            chat_doc = {
                "title": title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "message_count": 0
            }
            
            result = await self.chats_collection.insert_one(chat_doc)
            chat_id = str(result.inserted_id)
            
            logger.info(f"Created new chat with ID: {chat_id}")
            return chat_id
            
        except Exception as e:
            logger.error(f"Error creating chat: {e}")
            raise
    
    async def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a chat by ID.
        
        Args:
            chat_id: The chat ID
            
        Returns:
            Chat document or None if not found
        """
        try:
            chat = await self.chats_collection.find_one({"_id": ObjectId(chat_id)})
            if chat:
                chat["_id"] = str(chat["_id"])
            return chat
            
        except Exception as e:
            logger.error(f"Error getting chat {chat_id}: {e}")
            return None
    
    async def get_all_chats(self) -> List[Dict[str, Any]]:
        """
        Get all chats.
        
        Returns:
            List of chat documents
        """
        try:
            cursor = self.chats_collection.find().sort("updated_at", -1)
            chats = []
            async for chat in cursor:
                chat["_id"] = str(chat["_id"])
                chats.append(chat)
            
            logger.info(f"Retrieved {len(chats)} chats")
            return chats
            
        except Exception as e:
            logger.error(f"Error getting all chats: {e}")
            return []
    
    async def add_message(self, chat_id: str, role: str, content: str) -> str:
        """
        Add a message to a chat.
        
        Args:
            chat_id: The chat ID
            role: The message role (user/assistant)
            content: The message content
            
        Returns:
            The message ID as a string
        """
        try:
            message_doc = {
                "chat_id": ObjectId(chat_id),
                "role": role,
                "content": content,
                "created_at": datetime.utcnow()
            }
            
            result = await self.messages_collection.insert_one(message_doc)
            message_id = str(result.inserted_id)
            
            # Update chat's message count and updated_at
            await self.chats_collection.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$inc": {"message_count": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            logger.info(f"Added message to chat {chat_id}: {role}")
            return message_id
            
        except Exception as e:
            logger.error(f"Error adding message to chat {chat_id}: {e}")
            raise
    
    async def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat.
        
        Args:
            chat_id: The chat ID
            
        Returns:
            List of message documents
        """
        try:
            cursor = self.messages_collection.find({"chat_id": ObjectId(chat_id)}).sort("created_at", 1)
            messages = []
            async for message in cursor:
                message["_id"] = str(message["_id"])
                message["chat_id"] = str(message["chat_id"])
                messages.append(message)
            
            logger.info(f"Retrieved {len(messages)} messages for chat {chat_id}")
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages for chat {chat_id}: {e}")
            return []
    
    async def get_chat_history_for_agent(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        Get chat history in the format expected by the agent.
        
        Args:
            chat_id: The chat ID
            
        Returns:
            List of messages in agent format
        """
        try:
            messages = await self.get_chat_messages(chat_id)
            agent_history = []
            
            for message in messages:
                agent_history.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            
            return agent_history
            
        except Exception as e:
            logger.error(f"Error getting chat history for agent: {e}")
            return []
    
    async def update_chat_title(self, chat_id: str, title: str) -> bool:
        """
        Update the title of a chat.
        
        Args:
            chat_id: The chat ID
            title: The new title
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.chats_collection.update_one(
                {"_id": ObjectId(chat_id)},
                {"$set": {"title": title, "updated_at": datetime.utcnow()}}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated chat title for {chat_id}: {title}")
            else:
                logger.warning(f"Chat {chat_id} not found for title update")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating chat title for {chat_id}: {e}")
            return False
    
    async def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat and all its messages.
        
        Args:
            chat_id: The chat ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all messages for this chat
            await self.messages_collection.delete_many({"chat_id": ObjectId(chat_id)})
            
            # Delete the chat
            result = await self.chats_collection.delete_one({"_id": ObjectId(chat_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted chat {chat_id} and all its messages")
            else:
                logger.warning(f"Chat {chat_id} not found for deletion")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting chat {chat_id}: {e}")
            return False

# Global chat service instance
_chat_service: ChatService = None

def get_chat_service() -> ChatService:
    """Get the global chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service 