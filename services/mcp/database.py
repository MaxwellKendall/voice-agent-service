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

    def save_recipe_for_user(self, user_id: str, recipe_id: str) -> bool:
        """Save a recipe for a specific user."""
        try:
            # Check if recipe exists
            recipe = self.get_recipe(recipe_id)
            if not recipe:
                logger.error(f"Recipe {recipe_id} not found")
                raise Exception(f"Recipe {recipe_id} not found")
            
            # Use a separate collection for user saved recipes
            user_recipes_collection = self.db.user_saved_recipes
            
            # Check if already saved
            existing = user_recipes_collection.find_one({
                "user_id": user_id,
                "recipe_id": recipe_id
            })
            
            if existing:
                logger.info(f"Recipe {recipe_id} already saved for user {user_id}")
                return False
            
            # Save the recipe for the user
            user_recipe_doc = {
                "user_id": user_id,
                "recipe_id": recipe_id,
                "saved_at": datetime.utcnow(),
                "recipe_title": recipe.get("title", "Unknown"),
                "recipe_image": recipe.get("image_url", ""),
                "recipe_summary": recipe.get("summary", "")
            }
            
            user_recipes_collection.insert_one(user_recipe_doc)
            logger.info(f"Saved recipe {recipe_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving recipe for user: {e}")
            raise Exception(e.message)

    def get_user_saved_recipes_paginated(self, user_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get saved recipes for a specific user with pagination."""
        try:
            user_recipes_collection = self.db.user_saved_recipes
            
            # Calculate skip value for pagination
            skip = (page - 1) * limit
            
            # Get total count of saved recipes for the user
            total = user_recipes_collection.count_documents({"user_id": user_id})
            
            # Get paginated saved recipe IDs for the user
            saved_recipes = list(user_recipes_collection.find({"user_id": user_id})
                               .sort("saved_at", -1)  # Sort by saved_at descending
                               .skip(skip)
                               .limit(limit))
            
            # Fetch the full recipe data for each saved recipe
            full_recipes = []
            for saved_recipe in saved_recipes:
                recipe_id = saved_recipe["recipe_id"]
                recipe = self.get_recipe(recipe_id)
                if recipe:
                    # Add saved_at timestamp from user's saved recipe
                    recipe["saved_at"] = saved_recipe["saved_at"]
                    recipe["id"] = recipe_id  # Ensure ID is included
                    recipe.pop("_id", None)
                    full_recipes.append(recipe)
            
            # Calculate pagination info
            total_pages = (total + limit - 1) // limit  # Ceiling division
            has_next = page < total_pages
            has_prev = page > 1
            
            logger.info(f"Retrieved {len(full_recipes)} saved recipes for user {user_id} (page {page}/{total_pages})")
            
            return {
                "recipes": full_recipes,
                "total": total,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
            
        except Exception as e:
            logger.error(f"Error getting user saved recipes with pagination: {e}")
            return {
                "recipes": [],
                "total": 0,
                "total_pages": 0,
                "has_next": False,
                "has_prev": False
            }

    def remove_saved_recipe(self, user_id: str, recipe_id: str) -> bool:
        """Remove a saved recipe for a specific user."""
        try:
            user_recipes_collection = self.db.user_saved_recipes
            
            result = user_recipes_collection.delete_one({
                "user_id": user_id,
                "recipe_id": recipe_id
            })
            
            if result.deleted_count > 0:
                logger.info(f"Removed recipe {recipe_id} from user {user_id}'s saved recipes")
                return True
            else:
                logger.info(f"Recipe {recipe_id} not found in user {user_id}'s saved recipes")
                return False
                
        except Exception as e:
            logger.error(f"Error removing saved recipe: {e}")
            return False

    def is_recipe_saved_for_user(self, user_id: str, recipe_id: str) -> bool:
        """Check if a recipe is saved for a specific user."""
        try:
            user_recipes_collection = self.db.user_saved_recipes
            
            existing = user_recipes_collection.find_one({
                "user_id": user_id,
                "recipe_id": recipe_id
            })
            
            return existing is not None
            
        except Exception as e:
            logger.error(f"Error checking if recipe is saved: {e}")
            return False

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