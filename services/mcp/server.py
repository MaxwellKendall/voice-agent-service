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
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.responses import JSONResponse
import asyncio

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import our database and tools
from database import get_vector_store, get_mongodb_store
from embeddings import embed_query

# OpenAI API key for ephemeral key generation
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Create FastMCP server
mcp = FastMCP(name="recipe-agent")

# Add debug logging to see when tools are called
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def add_cors_headers(response):
    """Add CORS headers to a response."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# health check endpoint
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    logger.debug(f"health_check called with request: '{request}'")
    """Health check endpoint for Railway deployment."""
    response = PlainTextResponse("OK")
    return add_cors_headers(response)

# ephemeral API key endpoint
@mcp.custom_route("/generate-ephemeral-key", methods=["POST", "OPTIONS"])
async def generate_ephemeral_key(request: Request):
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
                    result = {
                        "success": True,
                        "api_key": ephemeral_key,
                        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
                    }
                else:
                    logger.error("No ephemeral key found in response")
                    result = {
                        "success": False,
                        "error": "No ephemeral key found in OpenAI response"
                    }
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                result = {
                    "success": False,
                    "error": f"OpenAI API error: {response.status_code}"
                }
        
        response = JSONResponse(result)
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Failed to generate ephemeral key: {e}")
        result = {
            "success": False,
            "error": str(e)
        }
        response = JSONResponse(result, status_code=500)
        return add_cors_headers(response)

# recipe extraction endpoint
@mcp.custom_route("/extract-recipe", methods=["POST"])
async def extract_recipe_endpoint(request: Request):
    """Extract and store recipe from URL via HTTP endpoint."""
    logger.debug(f"extract_recipe_endpoint called with request: '{request}'")
    try:
        # Parse JSON body
        body = await request.json()
        url = body.get("url")
        
        if not url:
            response = PlainTextResponse("Missing 'url' parameter", status_code=400)
            return add_cors_headers(response)
        
        # Call the implementation logic directly (not the decorated tool function)
        from tools import extract_recipe_data, enrich_recipe_with_ai, generate_embedding_prompt
        
        # Extract recipe content
        recipe_data = extract_recipe_data(url)
        recipe_data["link"] = url
        if not recipe_data:
            response = JSONResponse({
                "success": False,
                "error": f"Could not extract recipe content from URL: {url}"
            }, status_code=400)
            return add_cors_headers(response)
                
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
        
        result = {
            "success": True,
            "recipe_id": recipe_id,
            "title": enriched_data.get("title", "Unknown"),
            "link": url,
            "summary": enriched_data.get("summary", ""),
            "ingredients": enriched_data.get("ingredients", []),
            "instructions": enriched_data.get("instruction_details", []),
            "cuisine": enriched_data.get("cuisine", "Unknown"),
            "category": enriched_data.get("category", "Unknown"),
            "difficulty_level": enriched_data.get("difficulty_level", 0),
            "servings": enriched_data.get("servings", 0),
            "prep_time": enriched_data.get("prep_time", 0),
            "cook_time": enriched_data.get("cook_time", 0),
        }
        
        # Return JSON response
        response = JSONResponse(result)
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error in extract_recipe_endpoint: {e}")
        response = JSONResponse({"success": False, "error": str(e)}, status_code=500)
        return add_cors_headers(response)

# CORS preflight endpoint for extract-recipe
@mcp.custom_route("/extract-recipe", methods=["OPTIONS"])
async def extract_recipe_options(request: Request):
    """Handle CORS preflight requests for the extract-recipe endpoint."""
    logger.debug(f"extract_recipe_options called with request: '{request}'")
    response = PlainTextResponse("", status_code=200)
    return add_cors_headers(response)

# recipe by ID endpoint
@mcp.custom_route("/recipe/{recipe_id}", methods=["GET"])
async def get_recipe_by_id_endpoint(request: Request):
    """Get a recipe by its ID and return it as JSON."""
    recipe_id = request.path_params.get('recipe_id');
    logger.debug(f"get_recipe_by_id called with recipe_id: '{recipe_id}'")
    try:
        # Get the recipe from MongoDB
        mongo_store = get_mongodb_store()
        recipe = mongo_store.get_recipe(recipe_id)
        
        if not recipe:
            response = JSONResponse({
                "success": False,
                "error": f"Recipe with ID '{recipe_id}' not found"
            }, status_code=404)
            return add_cors_headers(response)
        
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
        response = JSONResponse({
            "success": True,
            "recipe": recipe
        })
        return add_cors_headers(response)
        
    except Exception as e:
        logger.error(f"Error fetching recipe {recipe_id}: {e}")
        response = JSONResponse({
            "success": False,
            "error": f"Failed to fetch recipe: {str(e)}"
        }, status_code=500)
        return add_cors_headers(response)

# CORS preflight endpoint for recipe by ID
@mcp.custom_route("/recipe/{recipe_id}", methods=["OPTIONS"])
async def get_recipe_by_id_options(request: Request):
    """Handle CORS preflight requests for the recipe by ID endpoint."""
    logger.debug(f"get_recipe_by_id_options called")
    response = PlainTextResponse("", status_code=200)
    return add_cors_headers(response)

@mcp.resource("data://recipe/{recipe_id}")
async def recipe_resource(recipe_id: str) -> dict:
    """Fetch a recipe from MongoDB by its ID."""
    logger.debug(f"recipe_resource called with recipe_id: '{recipe_id}'")
    try:
        # Get the recipe from MongoDB
        mongo_store = get_mongodb_store()
        recipe = mongo_store.get_recipe(recipe_id)
        
        if not recipe:
            raise ValueError(f"Recipe with ID '{recipe_id}' not found")
        
        return recipe
        
    except Exception as e:
        logger.error(f"Error fetching recipe {recipe_id}: {e}")
        raise ValueError(f"Failed to fetch recipe: {str(e)}")

@mcp.tool
def get_recipe_by_id(recipe_id: str) -> dict:
    """Fetch a recipe from MongoDB by its ID."""
    logger.debug(f"get_recipe_by_id called with recipe_id: '{recipe_id}'")
    try:
        # Get the recipe from MongoDB
        mongo_store = get_mongodb_store()
        recipe = mongo_store.get_recipe(recipe_id)
        recipe["_id"] = recipe_id

        if not recipe:
            raise ValueError(f"Recipe with ID '{recipe_id}' not found")
        
        return recipe
        
    except Exception as e:
        logger.error(f"Error fetching recipe {recipe_id}: {e}")
        raise ValueError(f"Failed to fetch recipe: {str(e)}")

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

@mcp.tool
def find_similar_recipes_from_url(recipe_url: str) -> List[Dict[str, Any]]:
    """
    @TODO: this should first check mongo to see if we have the recipe via the URL.
    Find recipes similar to a recipe from a web URL using vector similarity.
    
    Args:
        recipe_url: The URL of the recipe to find similar recipes for
        
    Returns:
        A list of similar recipes based on vector similarity
    """
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

@mcp.tool
async def extract_and_store_recipe(url: str) -> Dict[str, Any]:
    """
    Extract recipe content from a URL, enrich with AI, and store in databases.
    
    Args:
        url: The URL of the recipe to extract and store
        
    Returns:
        Dictionary with success status and recipe information
    """
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
    mcp.run(transport="http", host="0.0.0.0", port=8000, stateless_http=True) 