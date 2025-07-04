"""Custom tools for the AI agent."""

from typing import List, Dict, Any
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
import logging
import requests
from bs4 import BeautifulSoup
import re

from app.vector_store import get_vector_store

logger = logging.getLogger(__name__)

# Global embeddings instance
_embeddings: OpenAIEmbeddings = None

def get_embeddings() -> OpenAIEmbeddings:
    """Get or create the global embeddings instance."""
    global _embeddings
    if _embeddings is None:
        from app.config import get_openai_api_key
        _embeddings = OpenAIEmbeddings(openai_api_key=get_openai_api_key())
    return _embeddings

def extract_recipe_content(url: str) -> str:
    """
    Extract recipe content from a web URL, requiring JSON-LD structured data.
    
    Args:
        url: The URL of the recipe to extract content from
        
    Returns:
        Extracted recipe text content from JSON-LD, or error message if not found
    """
    try:
        logger.info(f"Extracting recipe content from: {url}")
        
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract JSON-LD structured data
        json_ld_data = extract_json_ld_recipe(soup)
        if json_ld_data:
            logger.info("Found JSON-LD recipe data, using structured extraction")
            return json_ld_data
        else:
            logger.warning("No JSON-LD recipe data found")
            return f"Error: No JSON-LD recipe data found on {url}. This tool requires structured recipe data."
        
    except Exception as e:
        logger.error(f"Error extracting recipe content from {url}: {e}")
        return f"Error: Failed to extract recipe content from {url}: {str(e)}"

def extract_json_ld_recipe(soup: BeautifulSoup) -> str:
    """
    Extract recipe information from JSON-LD structured data.
    
    Args:
        soup: BeautifulSoup object of the webpage
        
    Returns:
        Formatted recipe content from JSON-LD data
    """
    try:
        # Find all script tags with JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_ld_scripts:
            try:
                import json
                data = json.loads(script.string)
                
                # Handle both single objects and arrays
                if isinstance(data, list):
                    # Look for recipe objects in the array
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
    """
    Format recipe data from JSON-LD into a readable string.
    
    Args:
        recipe_data: Recipe data from JSON-LD
        
    Returns:
        Formatted recipe content
    """
    try:
        content_parts = []
        
        # Recipe name
        name = recipe_data.get('name', '')
        if name:
            content_parts.append(f"Recipe: {name}")
        
        # Description
        description = recipe_data.get('description', '')
        if description:
            content_parts.append(f"Description: {description}")
        
        # Category/cuisine
        recipe_category = recipe_data.get('recipeCategory', '')
        if recipe_category:
            content_parts.append(f"Category: {recipe_category}")
        
        recipe_cuisine = recipe_data.get('recipeCuisine', '')
        if recipe_cuisine:
            content_parts.append(f"Cuisine: {recipe_cuisine}")
        
        # Keywords
        keywords = recipe_data.get('keywords', '')
        if keywords:
            content_parts.append(f"Keywords: {keywords}")
        
        # Ingredients
        ingredients = recipe_data.get('recipeIngredient', [])
        if ingredients:
            content_parts.append("Ingredients:")
            for ingredient in ingredients:
                content_parts.append(f"- {ingredient}")
        
        # Combine all parts
        recipe_content = "\n".join(content_parts)
        
        # Limit content length to avoid token limits
        if len(recipe_content) > 4000:
            recipe_content = recipe_content[:4000] + "..."
        
        logger.info(f"Successfully extracted structured recipe data: {len(recipe_content)} characters")
        return recipe_content
        
    except Exception as e:
        logger.error(f"Error formatting recipe from JSON-LD: {e}")
        return None

@tool
def search_recipes(query: str) -> List[Dict[str, Any]]:
    """
    Search for recipes using a natural language query.
    
    Args:
        query: A natural language description of the recipes you want to find
        
    Returns:
        A list of up to 5 recipes with title, summary, url, and relevance score
    """
    try:
        logger.info(f"Searching recipes with query: {query}")
        
        # Get embeddings for the query
        embeddings = get_embeddings()
        query_vector = embeddings.embed_query(query)
        
        # Search the vector store
        vector_store = get_vector_store()
        recipes = vector_store.search_recipes(query_vector, limit=5)
        
        logger.info(f"Found {len(recipes)} recipes for query: {query}")
        return recipes
        
    except Exception as e:
        logger.error(f"Error in search_recipes: {e}")
        return []

@tool
def get_similar_recipes(recipe_id: str) -> List[Dict[str, Any]]:
    """
    Find recipes similar to a specific recipe by its ID.
    
    Args:
        recipe_id: The unique identifier of the recipe to find similar recipes for
        
    Returns:
        A list of up to 5 similar recipes with title, summary, url, and similarity score
    """
    try:
        logger.info(f"Finding similar recipes for recipe ID: {recipe_id}")
        
        # Get similar recipes from vector store
        vector_store = get_vector_store()
        similar_recipes = vector_store.get_similar_recipes(recipe_id, limit=5)
        
        logger.info(f"Found {len(similar_recipes)} similar recipes for recipe {recipe_id}")
        return similar_recipes
        
    except Exception as e:
        logger.error(f"Error in get_similar_recipes: {e}")
        return []

@tool
def find_similar_recipes_from_url(recipe_url: str) -> List[Dict[str, Any]]:
    """
    Find recipes similar to a recipe from a web URL by extracting its content and searching the database.
    
    Args:
        recipe_url: The URL of the recipe to find similar recipes for
        
    Returns:
        A list of up to 5 similar recipes with title, summary, url, and similarity score
    """
    try:
        logger.info(f"Finding similar recipes for URL: {recipe_url}")
        
        # Extract recipe content from the URL
        recipe_content = extract_recipe_content(recipe_url)
        
        # Get embeddings for the recipe content
        embeddings = get_embeddings()
        recipe_vector = embeddings.embed_query(recipe_content)
        
        # Search the vector store for similar recipes
        vector_store = get_vector_store()
        similar_recipes = vector_store.search_recipes(recipe_vector, limit=5)
        
        logger.info(f"Found {len(similar_recipes)} similar recipes for URL: {recipe_url}")
        return similar_recipes
        
    except Exception as e:
        logger.error(f"Error in find_similar_recipes_from_url: {e}")
        return []

@tool
def search_recipes_with_web_context(query: str) -> List[Dict[str, Any]]:
    """
    Search for recipes using a natural language query and enhance results with web search context.
    
    Args:
        query: A natural language description of the recipes you want to find
        
    Returns:
        A list of recipes with enhanced context from web search
    """
    try:
        logger.info(f"Searching recipes with web context for query: {query}")
        
        # First, search our database
        embeddings = get_embeddings()
        query_vector = embeddings.embed_query(query)
        vector_store = get_vector_store()
        recipes = vector_store.search_recipes(query_vector, limit=3)
        
        # If we have recipes, enhance them with web search
        if recipes:
            # Use web search to get additional context about the query
            from app.agent import create_web_search_tool
            web_search_tool = create_web_search_tool()
            
            # Search for current trends and tips related to the query
            web_context = web_search_tool.run(f"latest trends and tips for {query}")
            
            # Add web context to the response
            enhanced_recipes = []
            for recipe in recipes:
                enhanced_recipe = recipe.copy()
                enhanced_recipe['web_context'] = web_context[:200] + "..." if len(web_context) > 200 else web_context
                enhanced_recipes.append(enhanced_recipe)
            
            logger.info(f"Enhanced {len(enhanced_recipes)} recipes with web context")
            return enhanced_recipes
        
        return recipes
        
    except Exception as e:
        logger.error(f"Error in search_recipes_with_web_context: {e}")
        return []

def get_available_tools() -> List:
    """Get all available tools for the agent."""
    return [
        search_recipes, 
        get_similar_recipes, 
        find_similar_recipes_from_url,
        search_recipes_with_web_context
    ] 