#!/usr/bin/env python3
"""
Recipe Agent MCP Server using FastAPI with FastMCP mounted.
"""

import os
import random
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
import asyncio
import uvicorn

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our database and tools
from database import get_vector_store, get_mongodb_store
from embeddings import embed_query

# Add debug logging to see when tools are called
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# OpenAI API key for ephemeral key generation
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Create FastAPI app
api = FastAPI(title="Recipe Agent API", version="1.0.0")

# Add CORS middleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create FastMCP server
mcp = FastMCP(name="recipe-agent")

"""
Basic functions called by tools and exposed as endpoints.
"""

async def _search_recipes(query: str) -> List[Dict[str, Any]]:
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

async def _get_recipe_by_id(recipe_id: str) -> dict:
    logger.debug(f"get_recipe_by_id called with recipe_id: '{recipe_id}'")
    try:
        # Get the recipe from MongoDB
        mongo_store = get_mongodb_store()
        recipe = mongo_store.get_recipe(recipe_id)
        
        if not recipe:
            raise ValueError(f"Recipe with ID '{recipe_id}' not found")
        
        recipe["_id"] = recipe_id
        # Normalize ingredients - handle both string and array formats
        ingredients = recipe.get("ingredients", "")
        if isinstance(ingredients, str):
            recipe["ingredients"] = [ingredient.strip() for ingredient in ingredients.split('\n') if ingredient.strip()]
        elif isinstance(ingredients, list):
            recipe["ingredients"] = [str(ingredient).strip() for ingredient in ingredients if str(ingredient).strip()]
        else:
            recipe["ingredients"] = []
        
        # Convert datetime objects to ISO format strings for JSON serialization
        for key, value in recipe.items():
            if hasattr(value, 'isoformat'):  # Check if it's a datetime object
                recipe[key] = value.isoformat()
        
        # Return the recipe as JSON
        return recipe
    except Exception as e:
        logger.error(f"Error fetching recipe {recipe_id}: {e}")
        raise ValueError(f"Failed to fetch recipe: {str(e)}")

async def _get_similar_recipes(recipe_id: str) -> List[Dict[str, Any]]:
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
        
        # Use embedding_prompt if available (new approach), otherwise fall back to old approach
        if original_recipe.get('embedding_prompt'):
            # Use the stored embedding_prompt for consistent semantic search
            recipe_text = original_recipe['embedding_prompt']
            logger.debug(f"Using embedding_prompt for vector search")
        else:
            # Fallback for recipes without embedding_prompt (backward compatibility)
            recipe_text = f"{original_recipe.get('title', '')} {original_recipe.get('summary', '')} {' '.join(original_recipe.get('ingredients', []))}"
            logger.debug(f"Using fallback text for vector search (no embedding_prompt)")
        
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

async def _find_similar_recipes_from_url(recipe_url: str) -> List[Dict[str, Any]]:
    """
    Find recipes similar to a recipe from a web URL using vector similarity.
    
    Args:
        recipe_url: The URL of the webpage containing the recipe to find similar recipes for
        
    Returns:
        A list of similar recipes based on vector similarity
    """
    logger.debug(f"find_similar_recipes_from_url called with recipe_url: '{recipe_url}'")
    try:
        # Extract recipe content from URL
        from tools import extract_recipe_data, enrich_recipe_with_ai, generate_embedding_prompt
        recipe_data = extract_recipe_data(recipe_url)
        if not recipe_data:
            return []
        
        # Enrich with AI to get the same data structure as stored recipes
        enriched_data = asyncio.run(enrich_recipe_with_ai(recipe_data))
        
        # Generate natural language summary (embedding_prompt) for vector search
        # This ensures we're searching with the same semantic representation
        embedding_prompt = asyncio.run(generate_embedding_prompt(enriched_data))
        
        # Get embeddings for the recipe using the embedding_prompt
        recipe_vector = embed_query(embedding_prompt)
        
        # Search for similar recipes using vector similarity (Qdrant)
        vector_store = get_vector_store()
        similar_recipes = vector_store.search_recipes(recipe_vector, limit=5)
        
        return similar_recipes
        
    except Exception as e:
        logger.error(f"Error finding similar recipes from URL: {e}")
        return []

async def _extract_and_store_recipe(url: str) -> Dict[str, Any]:
    """
    Extract recipe content from a URL, enrich with AI, and store in databases.
    
    Args:
        url: The URL of the webpage containing the recipe
        
    Returns:
        A dictionary containing the extracted and stored recipe information
    """
    logger.debug(f"extract_and_store_recipe called with url: '{url}'")
    try:
        from tools import extract_recipe_data, enrich_recipe_with_ai, generate_embedding_prompt
        
        # Extract recipe content
        recipe_data = extract_recipe_data(url)
        if not recipe_data:
            return {
                "success": False,
                "error": f"Could not extract recipe content from URL: {url}"
            }
        
        # Enrich with AI
        enriched_data = await enrich_recipe_with_ai(recipe_data)
        
        # Generate natural language summary (embedding_prompt) for vector search
        # This matches the TypeScript approach exactly
        embedding_prompt = await generate_embedding_prompt(enriched_data)
        
        # Save to MongoDB with embedding_prompt
        mongo_store = get_mongodb_store()
        recipe_id = mongo_store.save_recipe(enriched_data, embedding_prompt)
        
        # Generate embeddings using ONLY the embedding_prompt (not the full recipe text)
        # This ensures identical semantic meaning with the TypeScript implementation
        recipe_vector = embed_query(embedding_prompt)
        
        # Store in vector store with full recipe data as metadata
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
        logger.error(f"Error in extract_and_store_recipe: {e}")
        return {
            "success": False,
            "error": str(e)
        }


"""
FastAPI Routes (replacing @custom_route decorators)
"""

@api.post("/generate-ephemeral-key")
async def generate_ephemeral_key():
    """Generate an ephemeral API key for client-side OpenAI Realtime API usage."""
    logger.debug("generate_ephemeral_key called")
    try:
        import httpx
        from datetime import datetime, timedelta
        
        # Call OpenAI's ephemeral key generation endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/realtime/sessions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-realtime-preview-2025-06-03"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                ephemeral_key = data.get("client_secret", {}).get("value")
                
                if ephemeral_key:
                    logger.info("Successfully generated ephemeral API key")
                    return {
                        "success": True,
                        "api_key": ephemeral_key,
                        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
                    }
                else:
                    logger.error("No ephemeral key found in response")
                    return {
                        "success": False,
                        "error": "No ephemeral key found in OpenAI response"
                    }
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"OpenAI API error: {response.status_code}"
                }
        
    except Exception as e:
        logger.error(f"Failed to generate ephemeral key: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )

@api.get("/recipe/{recipe_id}")
async def get_recipe_by_id_endpoint(recipe_id: str):
    """Get a recipe by its ID and return it as JSON."""
    try:
        recipe = await _get_recipe_by_id(recipe_id)
        return {
            "success": True,
            "recipe": recipe
        }
        
    except Exception as e:
        logger.error(f"Error fetching recipe {recipe_id}: {e}")
        return JSONResponse(
            {"success": False, "error": f"Failed to fetch recipe: {str(e)}"},
            status_code=500
        )

@api.post("/search-recipes")
async def search_recipes_endpoint(request: Request):
    """Search for recipes using natural language queries."""
    logger.debug("search_recipes_endpoint called")
    try:
        body = await request.json()
        query = body.get("query")
        
        if not query:
            return JSONResponse(
                {"success": False, "error": "Missing 'query' parameter"},
                status_code=400
            )
        
        # Call the search_recipes implementation function
        recipes = await _search_recipes(query)
        
        return {
            "success": True,
            "recipes": recipes
        }
        
    except Exception as e:
        logger.error(f"Error in search_recipes_endpoint: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )

@api.get("/similar-recipes/{recipe_id}")
async def get_similar_recipes_endpoint(recipe_id: str):
    """Get recipes similar to a specific recipe."""
    logger.debug(f"get_similar_recipes_endpoint called with recipe_id: '{recipe_id}'")
    try:
        if not recipe_id:
            return JSONResponse(
                {"success": False, "error": "Missing recipe_id parameter"},
                status_code=400
            )
        
        # Call the get_similar_recipes implementation function
        similar_recipes = await _get_similar_recipes(recipe_id)
        
        return {
            "success": True,
            "similar_recipes": similar_recipes
        }
        
    except Exception as e:
        logger.error(f"Error in get_similar_recipes_endpoint: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )

@api.post("/similar-recipes-from-url")
async def find_similar_recipes_from_url_endpoint(request: Request):
    """Find recipes similar to a recipe from a web URL."""
    logger.debug("find_similar_recipes_from_url_endpoint called")
    try:
        body = await request.json()
        recipe_url = body.get("recipe_url")
        
        if not recipe_url:
            return JSONResponse(
                {"success": False, "error": "Missing 'recipe_url' parameter"},
                status_code=400
            )
        
        # Call the find_similar_recipes_from_url implementation function
        similar_recipes = await _find_similar_recipes_from_url(recipe_url)
        
        return {
            "success": True,
            "similar_recipes": similar_recipes
        }
        
    except Exception as e:
        logger.error(f"Error in find_similar_recipes_from_url_endpoint: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )

@api.post("/extract-and-store-recipe")
async def extract_and_store_recipe_endpoint(request: Request):
    """Extract recipe content from a URL, enrich with AI, and store in databases."""
    logger.debug("extract_and_store_recipe_endpoint called")
    try:
        body = await request.json()
        url = body.get("url")
        
        if not url:
            return JSONResponse(
                {"success": False, "error": "Missing 'url' parameter"},
                status_code=400
            )
        
        # Call the extract_and_store_recipe implementation function
        result = await _extract_and_store_recipe(url)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in extract_and_store_recipe_endpoint: {e}")
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )

"""
MCP Resources
"""

@mcp.resource("data://recipe/{recipe_id}")
async def recipe_resource(recipe_id: str) -> dict:
    """Fetch a recipe from MongoDB by its ID."""
    logger.debug(f"recipe_resource called with recipe_id: '{recipe_id}'")
    try:
        # Get the recipe from MongoDB
        mongo_store = get_mongodb_store()
        recipe = await mongo_store.get_recipe(recipe_id)
        
        if not recipe:
            raise ValueError(f"Recipe with ID '{recipe_id}' not found")
        
        return recipe
        
    except Exception as e:
        logger.error(f"Error fetching recipe {recipe_id}: {e}")
        raise ValueError(f"Failed to fetch recipe: {str(e)}")

"""
MCP Tools called by backend agents connecting to this MCP server.
"""
@mcp.tool
async def get_recipe_by_id(recipe_id: str) -> dict:
    """Fetch a recipe from MongoDB by its ID."""
    return await _get_recipe_by_id(recipe_id)

@mcp.tool
async def search_recipes(query: str) -> List[Dict[str, Any]]:
    """Search for recipes using natural language queries with vector similarity."""
    return await _search_recipes(query)

@mcp.tool
async def get_similar_recipes(recipe_id: str) -> List[Dict[str, Any]]:
    """Find recipes similar to a specific recipe using vector similarity."""
    return await _get_similar_recipes(recipe_id)

@mcp.tool
async def find_similar_recipes_from_url(recipe_url: str) -> List[Dict[str, Any]]:
    """Find recipes similar to a recipe from a web URL using vector similarity."""
    return await _find_similar_recipes_from_url(recipe_url)

@mcp.tool
async def extract_and_store_recipe(url: str) -> Dict[str, Any]:
    """Extract recipe content from a URL, enrich with AI, and store in databases."""
    return await _extract_and_store_recipe(url)

# Mount MCP at /mcp
api.mount("/mcp", mcp.http_app())

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
    logger.info("Starting Recipe Agent API Server...")
    uvicorn.run(api, host="0.0.0.0", port=8000)