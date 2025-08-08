"""Recipe tools for MCP server."""

import logging
import sys
import os
import uuid
import requests
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import json
import re

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import get_vector_store, get_mongodb_store
    from embeddings import get_embeddings, embed_query
except ImportError:
    # Try relative imports if running as module
    from .database import get_vector_store, get_mongodb_store
    from .embeddings import get_embeddings, embed_query

logger = logging.getLogger(__name__)

async def search_recipes(query: str) -> List[Dict[str, Any]]:
    """
    Search for recipes using a natural language query.
    
    Args:
        query: A natural language description of the recipes you want to find
        
    Returns:
        A list of recipes matching the query
    """
    try:
        logger.info(f"Searching recipes for query: {query}")
        
        # Get embeddings for the query
        embeddings_client = get_embeddings()
        query_vector = embed_query(query)
        
        # Search vector store (Qdrant)
        vector_store = get_vector_store()
        recipes = vector_store.search_recipes(query_vector, limit=5)
        
        logger.info(f"Found {len(recipes)} recipes for query: {query}")
        return recipes
        
    except Exception as e:
        logger.error(f"Error searching recipes: {e}")
        return []

async def get_similar_recipes(recipe_id: str) -> List[Dict[str, Any]]:
    """
    Find recipes similar to a specific recipe by its ID using vector similarity.
    
    Args:
        recipe_id: The unique identifier of the recipe to find similar recipes for
        
    Returns:
        A list of similar recipes based on vector similarity
    """
    try:
        logger.info(f"Finding similar recipes for recipe ID: {recipe_id}")
        
        # Get the original recipe from MongoDB
        mongo_store = get_mongodb_store()
        original_recipe = mongo_store.get_recipe(recipe_id)
        
        if not original_recipe:
            logger.warning(f"Recipe not found: {recipe_id}")
            return []
        
        # Create a text representation of the recipe for embedding
        recipe_text = f"{original_recipe.get('title', '')} {original_recipe.get('summary', '')} {' '.join(original_recipe.get('ingredients', []))}"
        
        # Get embeddings for the recipe
        embeddings_client = get_embeddings()
        recipe_vector = embed_query(recipe_text)
        
        # Search for similar recipes using vector similarity (Qdrant)
        vector_store = get_vector_store()
        similar_recipes = vector_store.search_recipes(recipe_vector, limit=5)
        
        # Filter out the original recipe from results
        similar_recipes = [r for r in similar_recipes if r.get('_id') != recipe_id]
        
        logger.info(f"Found {len(similar_recipes)} similar recipes for recipe ID: {recipe_id}")
        return similar_recipes
        
    except Exception as e:
        logger.error(f"Error finding similar recipes: {e}")
        return []

async def find_similar_recipes_from_url(recipe_url: str) -> List[Dict[str, Any]]:
    """
    Find recipes similar to a recipe from a web URL by extracting its content and searching the database.
    
    Args:
        recipe_url: The URL of the recipe to find similar recipes for
        
    Returns:
        A list of similar recipes based on vector similarity
    """
    try:
        logger.info(f"Finding similar recipes for URL: {recipe_url}")
        
        # Extract recipe content from URL
        recipe_content = extract_recipe_content(recipe_url)
        if not recipe_content:
            logger.warning(f"Could not extract recipe content from URL: {recipe_url}")
            return []
        
        # Parse the recipe content
        recipe_data = parse_recipe_content(recipe_content, recipe_url)
        
        # Create text representation for embedding
        recipe_text = f"{recipe_data.get('title', '')} {recipe_data.get('summary', '')} {' '.join(recipe_data.get('ingredients', []))}"
        
        # Get embeddings for the recipe
        embeddings_client = get_embeddings()
        recipe_vector = embed_query(recipe_text)
        
        # Search for similar recipes using vector similarity (Qdrant)
        vector_store = get_vector_store()
        similar_recipes = vector_store.search_recipes(recipe_vector, limit=5)
        
        logger.info(f"Found {len(similar_recipes)} similar recipes for URL: {recipe_url}")
        return similar_recipes
        
    except Exception as e:
        logger.error(f"Error finding similar recipes from URL: {e}")
        return []

async def extract_and_store_recipe(url: str) -> Dict[str, Any]:
    """
    Extract recipe content from a URL, enrich with AI, store in MongoDB, and add to vector database.
    
    Args:
        url: The URL of the recipe to extract and store
        
    Returns:
        Dictionary with success status and recipe information
    """
    try:
        logger.info(f"Extracting and storing recipe from URL: {url}")
        
        # Extract recipe content
        recipe_content = extract_recipe_content(url)
        if not recipe_content:
            return {
                "success": False,
                "error": f"Could not extract recipe content from URL: {url}"
            }
        
        # Parse recipe content
        recipe_data = parse_recipe_content(recipe_content, url)
        
        # Enrich with AI
        enriched_data = await enrich_recipe_with_ai(recipe_data)
        
        # Save to MongoDB
        mongo_store = get_mongodb_store()
        recipe_id = mongo_store.save_recipe(enriched_data)
        
        # Generate embeddings and save to vector store (Qdrant)
        embeddings_client = get_embeddings()
        recipe_text = f"{enriched_data.get('title', '')} {enriched_data.get('summary', '')} {' '.join(enriched_data.get('ingredients', []))}"
        recipe_vector = embed_query(recipe_text)
        
        vector_store = get_vector_store()
        vector_store.add_recipe(recipe_id, recipe_vector, enriched_data)
        
        logger.info(f"Successfully extracted and stored recipe: {recipe_id}")
        return {
            "success": True,
            "recipe_id": recipe_id,
            "title": enriched_data.get("title", "Unknown"),
            "url": url,
            "summary": enriched_data.get("summary", "")
        }
        
    except Exception as e:
        logger.error(f"Error extracting and storing recipe: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def extract_recipe_content(url: str) -> Optional[str]:
    """Extract recipe content from a web URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract JSON-LD structured data
        json_ld_data = extract_json_ld_recipe(soup)
        if json_ld_data:
            return json_ld_data
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting recipe content from {url}: {e}")
        return None

def extract_json_ld_recipe(soup: BeautifulSoup) -> Optional[str]:
    """Extract recipe information from JSON-LD structured data."""
    try:
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') == 'Recipe':
                            return format_recipe_from_json_ld(item)
                elif isinstance(data, dict) and data.get('@type') == 'Recipe':
                    return format_recipe_from_json_ld(data)
                    
            except (json.JSONDecodeError, AttributeError) as e:
                logger.warning(f"Error parsing JSON-LD script: {e}")
                continue
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting JSON-LD recipe data: {e}")
        return None

def format_recipe_from_json_ld(recipe_data: dict) -> str:
    """Format recipe data from JSON-LD."""
    try:
        title = recipe_data.get('name', 'Unknown Recipe')
        description = recipe_data.get('description', '')
        ingredients = recipe_data.get('recipeIngredient', [])
        instructions = recipe_data.get('recipeInstructions', [])
        
        # Format ingredients
        ingredients_text = '\n'.join([f"- {ingredient}" for ingredient in ingredients])
        
        # Format instructions
        if isinstance(instructions, list):
            instructions_text = '\n'.join([f"{i+1}. {step}" for i, step in enumerate(instructions)])
        else:
            instructions_text = instructions
        
        formatted_recipe = f"""
Title: {title}
Description: {description}

Ingredients:
{ingredients_text}

Instructions:
{instructions_text}
"""
        return formatted_recipe
        
    except Exception as e:
        logger.error(f"Error formatting recipe from JSON-LD: {e}")
        return ""

def parse_recipe_content(recipe_content: str, url: str) -> Dict[str, Any]:
    """Parse recipe content into structured data."""
    try:
        # Simple parsing - in a real implementation, you'd use more sophisticated parsing
        lines = recipe_content.split('\n')
        
        recipe_data = {
            "title": "Extracted Recipe",
            "url": url,
            "ingredients": [],
            "instructions": [],
            "source": extract_domain(url)
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Title:"):
                recipe_data["title"] = line.replace("Title:", "").strip()
            elif line.startswith("Description:"):
                recipe_data["summary"] = line.replace("Description:", "").strip()
            elif line == "Ingredients:":
                current_section = "ingredients"
            elif line == "Instructions:":
                current_section = "instructions"
            elif line.startswith("- ") and current_section == "ingredients":
                recipe_data["ingredients"].append(line[2:])
            elif line.startswith(("1.", "2.", "3.", "4.", "5.")) and current_section == "instructions":
                recipe_data["instructions"].append(line.split(". ", 1)[1] if ". " in line else line)
        
        return recipe_data
        
    except Exception as e:
        logger.error(f"Error parsing recipe content: {e}")
        return {"title": "Unknown Recipe", "url": url}

async def enrich_recipe_with_ai(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich recipe data with AI-generated information."""
    try:
        # Mock AI enrichment - in real implementation, call OpenAI API
        enriched_data = recipe_data.copy()
        
        # Add default values
        enriched_data.setdefault("cuisine", "Unknown")
        enriched_data.setdefault("category", "Main Dish")
        enriched_data.setdefault("difficulty_level", 3)
        enriched_data.setdefault("servings", 4)
        enriched_data.setdefault("prep_time", "30 minutes")
        enriched_data.setdefault("cook_time", "45 minutes")
        enriched_data.setdefault("rating", 4.0)
        enriched_data.setdefault("rating_count", 10)
        
        # Add relevance scores
        enriched_data["relevance"] = {
            "family": 0.8,
            "single": 0.6,
            "health": 0.7
        }
        
        return enriched_data
        
    except Exception as e:
        logger.error(f"Error enriching recipe with AI: {e}")
        return recipe_data

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "unknown"

def get_available_tools() -> List:
    """Get all available tools for the agent."""
    return [
        search_recipes,
        get_similar_recipes,
        find_similar_recipes_from_url,
        extract_and_store_recipe
    ] 