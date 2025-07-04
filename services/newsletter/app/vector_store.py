"""Vector store operations for recipe search using Qdrant."""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging

logger = logging.getLogger(__name__)

class RecipeVectorStore:
    """Handles vector operations for recipe search."""
    
    def __init__(self, url: str, api_key: Optional[str] = None):
        """Initialize Qdrant client."""
        self.client = QdrantClient(url=url, api_key=api_key)
        self.collection_name = "recipes"
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self) -> None:
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
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def search_recipes(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for recipes using a query vector."""
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            recipes = []
            for result in search_result:
                recipe = {
                    "id": result.id,
                    "title": result.payload.get("title", ""),
                    "summary": result.payload.get("summary", ""),
                    "url": result.payload.get("link", ""),
                    "score": result.score
                }
                recipes.append(recipe)
            
            logger.info(f"Found {len(recipes)} recipes for query")
            return recipes
            
        except Exception as e:
            logger.error(f"Error searching recipes: {e}")
            return []
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific recipe by ID."""
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[recipe_id]
            )
            
            if result:
                point = result[0]
                return {
                    "id": point.id,
                    "title": point.payload.get("title", ""),
                    "summary": point.payload.get("summary", ""),
                    "url": point.payload.get("url", ""),
                    "vector": point.vector
                }
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving recipe {recipe_id}: {e}")
            return None
    
    def get_similar_recipes(self, recipe_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recipes similar to a given recipe ID."""
        try:
            # First get the recipe vector
            recipe = self.get_recipe_by_id(recipe_id)
            if not recipe or not recipe.get("vector"):
                logger.warning(f"Recipe {recipe_id} not found or has no vector")
                return []
            
            # Search for similar recipes
            return self.search_recipes(recipe["vector"], limit)
            
        except Exception as e:
            logger.error(f"Error getting similar recipes for {recipe_id}: {e}")
            return []

# Global vector store instance
_vector_store: Optional[RecipeVectorStore] = None

def get_vector_store() -> RecipeVectorStore:
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        from app.config import get_vector_db_url, get_vector_db_api_key
        _vector_store = RecipeVectorStore(
            url=get_vector_db_url(),
            api_key=get_vector_db_api_key()
        )
    return _vector_store 