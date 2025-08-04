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

    def add_recipe(self, recipe_data: Dict[str, Any], recipe_vector: List[float]) -> str:
        """Add a recipe to the vector store conforming to RecipeVector schema."""
        try:
            import uuid
            
            # Generate a unique ID for the recipe
            recipe_id = str(uuid.uuid4())
            
            # Convert time strings to minutes for numeric fields
            prep_time_minutes = self._parse_time_to_minutes(recipe_data.get("prep_time", ""))
            cook_time_minutes = self._parse_time_to_minutes(recipe_data.get("cook_time", ""))
            
            # Convert servings to number
            servings = self._parse_servings(recipe_data.get("servings", ""))
            
            # Convert rating to number
            rating = self._parse_rating(recipe_data.get("rating", ""))
            rating_count = self._parse_rating_count(recipe_data.get("rating_count", ""))
            
            # Process relevance scores from AI enrichment
            relevance = recipe_data.get("relevance", {})
            if isinstance(relevance, dict):
                # Convert 1-10 scale to 0-1 scale for consistency
                family_relevance = relevance.get("family", 5) / 10.0
                single_relevance = relevance.get("single", 5) / 10.0
                health_relevance = relevance.get("health", 5) / 10.0
            else:
                # Fallback to default values
                family_relevance = 0.5
                single_relevance = 0.5
                health_relevance = 0.5
            
            # Create the point structure conforming to RecipeVector schema
            point = PointStruct(
                id=recipe_id,
                vector=recipe_vector,
                payload={
                    "mongo_id": recipe_id,  # Using recipe_id as mongo_id for now
                    "title": recipe_data.get("title", ""),
                    "summary": recipe_data.get("summary", ""),
                    "category": recipe_data.get("category", ""),
                    "cuisine": recipe_data.get("cuisine", ""),
                    "level_of_effort": self._calculate_effort_level(prep_time_minutes, cook_time_minutes),
                    "tools": recipe_data.get("tools", []),
                    "relevance": {
                        "family": family_relevance,
                        "single": single_relevance,
                        "health": health_relevance
                    },
                    "keywords": recipe_data.get("keywords", []),
                    "servings": servings,
                    "cook_time_minutes": cook_time_minutes,
                    "prep_time_minutes": prep_time_minutes,
                    "rating": rating,
                    "rating_count": rating_count,
                    "image_url": recipe_data.get("image_url", ""),
                    "source": recipe_data.get("source", ""),
                    "link": recipe_data.get("link", "")
                }
            )
            
            # Upsert the point (insert or update)
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.info(f"Successfully added recipe {recipe_id} to vector store")
            return recipe_id
            
        except Exception as e:
            logger.error(f"Error adding recipe to vector store: {e}")
            raise

    def _parse_time_to_minutes(self, time_str: str) -> int:
        """Parse time string to minutes."""
        if not time_str:
            return 0
        
        try:
            # Handle various time formats (PT30M, 30 min, 30 minutes, etc.)
            time_str = time_str.upper()
            
            # Remove common prefixes
            if time_str.startswith('PT'):
                time_str = time_str[2:]
            
            # Extract minutes
            if 'M' in time_str:
                minutes = int(time_str.split('M')[0])
            elif 'MIN' in time_str:
                minutes = int(time_str.split('MIN')[0])
            elif 'MINUTES' in time_str:
                minutes = int(time_str.split('MINUTES')[0])
            else:
                # Try to extract any number
                import re
                numbers = re.findall(r'\d+', time_str)
                minutes = int(numbers[0]) if numbers else 0
            
            return minutes
        except (ValueError, IndexError):
            return 0

    def _parse_servings(self, servings_str: str) -> int:
        """Parse servings string to number."""
        if not servings_str:
            return 1
        
        try:
            import re
            numbers = re.findall(r'\d+', servings_str)
            return int(numbers[0]) if numbers else 1
        except (ValueError, IndexError):
            return 1

    def _parse_rating(self, rating_str: str) -> float:
        """Parse rating string to float."""
        if not rating_str:
            return 0.0
        
        try:
            return float(rating_str)
        except (ValueError, TypeError):
            return 0.0

    def _parse_rating_count(self, count_str: str) -> int:
        """Parse rating count string to integer."""
        if not count_str:
            return 0
        
        try:
            return int(count_str)
        except (ValueError, TypeError):
            return 0

    def _calculate_effort_level(self, prep_minutes: int, cook_minutes: int) -> int:
        """Calculate effort level based on prep and cook time."""
        total_time = prep_minutes + cook_minutes
        
        if total_time <= 15:
            return 1  # Very easy
        elif total_time <= 30:
            return 2  # Easy
        elif total_time <= 60:
            return 3  # Medium
        elif total_time <= 120:
            return 4  # Hard
        else:
            return 5  # Very hard

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