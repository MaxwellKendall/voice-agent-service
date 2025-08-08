#!/usr/bin/env python3
"""
Recipe Agent MCP Server using FastMCP.
"""

import os
import random
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastmcp import FastMCP

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our database and tools
from database import get_vector_store, get_mongodb_store
from embeddings import embed_query

# Create FastMCP server
mcp = FastMCP(name="recipe-agent")

# Add debug logging to see when tools are called
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def roll_dice(n_dice: int) -> list[int]:
    """Roll `n_dice` 6-sided dice and return the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]

@mcp.tool
def search_recipes(query: str) -> List[Dict[str, Any]]:
    """
    Search for recipes using natural language queries with vector similarity.
    
    Args:
        query: Natural language description of recipes to find
        
    Returns:
        A list of recipes matching the query
    """
    logger.debug(f"search_recipes called with query: '{query}'")
    try:
        # Get embeddings for the query
        query_vector = embed_query(query)
        logger.debug(f"Got embeddings for query")
        
        # Search vector store (Qdrant)
        vector_store = get_vector_store()
        recipes = vector_store.search_recipes(query_vector, limit=5)
        logger.debug(f"Found {len(recipes)} recipes")
        
        return recipes
        
    except Exception as e:
        logger.error(f"Error searching recipes: {e}")
        return []

@mcp.tool
def get_similar_recipes(recipe_id: str) -> List[Dict[str, Any]]:
    """
    Find recipes similar to a specific recipe using vector similarity.
    
    Args:
        recipe_id: The unique identifier of the recipe to find similar recipes for
        
    Returns:
        A list of similar recipes based on vector similarity
    """
    logger.debug(f"get_similar_recipes called with recipe_id: '{recipe_id}'")
    try:
        # Get the original recipe from MongoDB
        mongo_store = get_mongodb_store()
        original_recipe = mongo_store.get_recipe(recipe_id)
        
        if not original_recipe:
            logger.debug(f"No original recipe found for ID: {recipe_id}")
            return []
        
        logger.debug(f"Found original recipe: {original_recipe.get('title', 'Unknown')}")
        
        # Create a text representation of the recipe for embedding
        recipe_text = f"{original_recipe.get('title', '')} {original_recipe.get('summary', '')} {' '.join(original_recipe.get('ingredients', []))}"
        
        # Get embeddings for the recipe
        recipe_vector = embed_query(recipe_text)
        logger.debug(f"Got embeddings for recipe")
        
        # Search for similar recipes using vector similarity (Qdrant)
        vector_store = get_vector_store()
        similar_recipes = vector_store.search_recipes(recipe_vector, limit=5)
        
        # Filter out the original recipe from results
        similar_recipes = [r for r in similar_recipes if r.get('_id') != recipe_id]
        logger.debug(f"Found {len(similar_recipes)} similar recipes")
        
        return similar_recipes
        
    except Exception as e:
        logger.error(f"Error finding similar recipes: {e}")
        return []

@mcp.tool
def find_similar_recipes_from_url(recipe_url: str) -> List[Dict[str, Any]]:
    """
    Find recipes similar to a recipe from a web URL using vector similarity.
    
    Args:
        recipe_url: The URL of the recipe to find similar recipes for
        
    Returns:
        A list of similar recipes based on vector similarity
    """
    try:
        # Extract recipe content from URL
        from tools import extract_recipe_content, parse_recipe_content
        recipe_content = extract_recipe_content(recipe_url)
        if not recipe_content:
            return []
        
        # Parse the recipe content
        recipe_data = parse_recipe_content(recipe_content, recipe_url)
        
        # Create text representation for embedding
        recipe_text = f"{recipe_data.get('title', '')} {recipe_data.get('summary', '')} {' '.join(recipe_data.get('ingredients', []))}"
        
        # Get embeddings for the recipe
        recipe_vector = embed_query(recipe_text)
        
        # Search for similar recipes using vector similarity (Qdrant)
        vector_store = get_vector_store()
        similar_recipes = vector_store.search_recipes(recipe_vector, limit=5)
        
        return similar_recipes
        
    except Exception as e:
        logger.error(f"Error finding similar recipes from URL: {e}")
        return []

@mcp.tool
def extract_and_store_recipe(url: str) -> Dict[str, Any]:
    """
    Extract recipe content from a URL, enrich with AI, and store in databases.
    
    Args:
        url: The URL of the recipe to extract and store
        
    Returns:
        Dictionary with success status and recipe information
    """
    try:
        from tools import extract_recipe_content, parse_recipe_content, enrich_recipe_with_ai
        
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
        enriched_data = enrich_recipe_with_ai(recipe_data)
        
        # Save to MongoDB
        mongo_store = get_mongodb_store()
        recipe_id = mongo_store.save_recipe(enriched_data)
        
        # Generate embeddings and save to vector store (Qdrant)
        recipe_text = f"{enriched_data.get('title', '')} {enriched_data.get('summary', '')} {' '.join(enriched_data.get('ingredients', []))}"
        recipe_vector = embed_query(recipe_text)
        
        vector_store = get_vector_store()
        vector_store.add_recipe(recipe_id, recipe_vector, enriched_data)
        
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

if __name__ == "__main__":
    # Validate configuration
    try:
        from config import config
        config.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    
    # Start server
    logger.info("Starting Recipe Agent MCP Server...")
    mcp.run(transport="http", port=8000, stateless_http=True) 