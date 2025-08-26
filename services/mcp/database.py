"""Database operations for MCP server - direct database connections."""

import logging
import sys
import os
from typing import Dict, Any, List, Optional
from bson import ObjectId
from pymongo import MongoClient
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
import uuid
from datetime import datetime

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import config
except ImportError:
    # Try relative imports if running as module
    from .config import config

logger = logging.getLogger(__name__)

# Global clients
_mongodb_client: Optional[MongoClient] = None
_qdrant_client: Optional[QdrantClient] = None

def get_mongodb_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _mongodb_client
    if _mongodb_client is None:
        _mongodb_client = MongoClient(config.MONGODB_URL)
        logger.info("MongoDB client initialized")
    return _mongodb_client

def get_qdrant_client() -> QdrantClient:
    """Get or create Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        print(f"QDRANT_URL: {config.QDRANT_URL}")
        print(f"QDRANT_API_KEY: {config.QDRANT_API_KEY}")
        _qdrant_client = QdrantClient(
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY
        )
        logger.info("Qdrant client initialized")
    return _qdrant_client

class VectorStore:
    """Vector store operations for recipes."""
    
    def __init__(self):
        self.client = get_qdrant_client()
        self.collection_name = "recipes"
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the recipes collection exists."""
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
    
    def search_recipes(self, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search recipes by vector similarity."""
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            recipes = []
            for result in results:
                recipe_data = result.payload
                recipe_data['score'] = result.score
                recipes.append(recipe_data)
            
            return recipes
        except Exception as e:
            logger.error(f"Error searching recipes: {e}")
            return []
    
    def _convert_to_qdrant_id(self, mongo_id: str) -> int:
        """Convert MongoDB ObjectId string to numeric ID suitable for Qdrant."""
        # Initialize a hash value
        hash_val = 0
        
        # Iterate over each character in the MongoDB ObjectId
        for char in mongo_id:
            char_code = ord(char)  # Get ASCII code of the character
            
            # Apply a basic hash function: 31 * hash + char
            # This is a common hash pattern used in languages like Java
            hash_val = ((hash_val << 5) - hash_val) + char_code
            
            # Force the hash into 32-bit signed integer range (Python equivalent of JS)
            hash_val = hash_val & 0xFFFFFFFF
        
        # Ensure the result is a positive integer (Qdrant doesn't allow negative IDs)
        # Also ensure it's within a reasonable range for Qdrant
        return abs(hash_val) % (2**31)  # Keep within 31-bit positive range

    def add_recipe(self, recipe_id: str, recipe_vector: List[float], recipe_data: Dict[str, Any]) -> bool:
        """Add a recipe to the vector store."""
        try:
            recipe_data["mongo_id"] = recipe_id
            point = PointStruct(
                id=self._convert_to_qdrant_id(recipe_id),
                vector=recipe_vector,
                payload=recipe_data
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Added recipe to vector store: {recipe_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding recipe to vector store: {e}")
            return False

class MongoDBStore:
    """MongoDB operations for recipes."""
    
    def __init__(self):
        self.client = get_mongodb_client()
        self.db = self.client.recipes
        self.collection = self.db.parsed_recipes
    
    def get_recipe(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get a recipe by ID."""
        try:
            recipe = self.collection.find_one({"_id": ObjectId(recipe_id)})
            return recipe
        except Exception as e:
            logger.error(f"Error getting recipe: {e}")
            return None
    
    def save_recipe(self, recipe_data: Dict[str, Any], embedding_prompt: Optional[str] = None) -> str:
        """Save a recipe to MongoDB."""
        try:
            if "_id" in recipe_data:
                recipe_data["_id"] = None
            
            # Add timestamps
            recipe_data["created_at"] = datetime.utcnow()
            recipe_data["updated_at"] = datetime.utcnow()
            
            # Add embedding_prompt if provided
            if embedding_prompt:
                recipe_data["embedding_prompt"] = embedding_prompt
                recipe_data["vector_embedded"] = True  # Mark as ready for vector embedding
            
            # Upsert the recipe ( for some reason the "link" is not defined, we also do not have category)
            doc = self.collection.find_one_and_replace(
                {"link": recipe_data["link"]},
                recipe_data,
                upsert=True,
                return_document=True
            )
            
            # Get the ID from the returned document
            recipe_id = str(doc["_id"])
            
            logger.info(f"Saved recipe to MongoDB: {recipe_id}")
            return recipe_id
        except Exception as e:
            logger.error(f"Error saving recipe: {e}")
            raise
    
    def find_similar_recipes(self, recipe_data: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar recipes based on attributes (not vector similarity)."""
        try:
            # Simple similarity search based on cuisine and category
            query = {}
            if recipe_data.get("cuisine"):
                query["cuisine"] = recipe_data["cuisine"]
            if recipe_data.get("category"):
                query["category"] = recipe_data["category"]
            
            if not query:
                # Fallback to general search
                query = {"qualified": True}
            
            recipes = list(self.collection.find(query).limit(limit))
            return recipes
        except Exception as e:
            logger.error(f"Error finding similar recipes: {e}")
            return []

# Global instances
_vector_store: Optional[VectorStore] = None
_mongodb_store: Optional[MongoDBStore] = None

def get_vector_store() -> VectorStore:
    """Get or create vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store

def get_mongodb_store() -> MongoDBStore:
    """Get or create MongoDB store instance."""
    global _mongodb_store
    if _mongodb_store is None:
        _mongodb_store = MongoDBStore()
    return _mongodb_store 