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
from openai import OpenAI
import asyncio

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import get_vector_store, get_mongodb_store
    from embeddings import get_embeddings, embed_query
    from config import config
    from prompts.recipe_enrichment import (
        RECIPE_ENRICHMENT_PROMPT,
        RECIPE_ENRICHMENT_SYSTEM_PROMPT,
        RECIPE_ENRICHMENT_JSON_SCHEMA
    )
except ImportError:
    # Try relative imports if running as module
    from .database import get_vector_store, get_mongodb_store
    from .embeddings import get_embeddings, embed_query
    from .config import config
    from .prompts.recipe_enrichment import (
        RECIPE_ENRICHMENT_PROMPT,
        RECIPE_ENRICHMENT_SYSTEM_PROMPT,
        RECIPE_ENRICHMENT_JSON_SCHEMA
    )

logger = logging.getLogger(__name__)

# Initialize OpenAI client for chat completions
_openai_client: OpenAI = None

def get_openai_client() -> OpenAI:
    """Get or create OpenAI client for chat completions."""
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        logger.info("OpenAI chat client initialized")
    return _openai_client

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
        recipe_data = extract_recipe_data(recipe_url)
        if not recipe_data:
            logger.warning(f"Could not extract recipe content from URL: {recipe_url}")
            return []
        
        
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
        recipe_data = extract_recipe_data(url)
        if not recipe_data:
            return {
                "success": False,
                "error": f"Could not extract recipe content from URL: {url}"
            }
        
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

async def generate_embedding_prompt(recipe_data: Dict[str, Any]) -> str:
    """
    Generate a natural language summary (embedding_prompt) for vector search.
    This matches the TypeScript implementation exactly.
    
    Args:
        recipe_data: The enriched recipe data
        
    Returns:
        A natural language summary suitable for embedding
    """
    try:
        # Extract ingredients list (clean up the string)
        ingredients = recipe_data.get('ingredients', [])
        if isinstance(ingredients, list):
            ingredients_list = ingredients
        else:
            ingredients_list = [str(ingredients)]
        
        # Parse time strings to minutes (handle various formats)
        prep_time = recipe_data.get('prep_time', '0')
        cook_time = recipe_data.get('cook_time', '0')
        
        def parse_time_to_minutes(time_str):
            if not time_str:
                return 0
            if isinstance(time_str, int):
                return time_str
            if isinstance(time_str, str):
                # Handle PT5M format
                import re
                match = re.match(r'PT(\d+)M', time_str)
                if match:
                    return int(match.group(1))
                # Handle "30 minutes" format
                match = re.match(r'(\d+)', time_str)
                if match:
                    return int(match.group(1))
            return 0
        
        prep_time_minutes = parse_time_to_minutes(prep_time)
        cook_time_minutes = parse_time_to_minutes(cook_time)
        
        # Get relevance scores
        relevance = recipe_data.get('relevance', {})
        family_score = relevance.get('family', 5) if isinstance(relevance, dict) else 5
        single_score = relevance.get('single', 5) if isinstance(relevance, dict) else 5
        health_score = relevance.get('health', 5) if isinstance(relevance, dict) else 5
        
        # Get nutrition info
        nutrients = recipe_data.get('nutrients', {})
        calories = nutrients.get('calories', 'N/A') if isinstance(nutrients, dict) else 'N/A'
        protein = nutrients.get('proteinContent', 'N/A') if isinstance(nutrients, dict) else 'N/A'
        carbs = nutrients.get('carbohydrateContent', 'N/A') if isinstance(nutrients, dict) else 'N/A'
        fat = nutrients.get('fatContent', 'N/A') if isinstance(nutrients, dict) else 'N/A'
        
        system_prompt = """You are a friendly home cook summarizing recipes for a smart recommendation system.

Write a **2–3 sentence summary** that:
- Explains what the dish is and why it's appealing (e.g., bold flavor, easy cleanup, kid-friendly)
- Highlights key features like main-ingredients, cooking method, cuisine, and type of meal (e.g., main, salad, soup, side, dessert)
- Suggests an ideal context for the recipe: occasion (e.g., weeknight dinner, casual party), season (e.g., summer, fall), or weather (e.g., chilly day comfort food)
- Optionally comment on health profile (e.g., high protein, low-carb, veggie-packed)
- Comment on the recipe's difficulty level (e.g., easy, medium, hard) and choose an ideal persona (e.g., family, single, health)
- Feels conversational and natural — as if you're texting a friend who wants ideas

Avoid repeating the recipe title. Be concise, and expressive."""

        # Prepare instructions text to avoid f-string backslash issue
        instructions_text = '\n'.join(recipe_data.get('instruction', []))
        
        user_prompt = f"""
Recipe Title: {recipe_data.get('title', 'Unknown')}
Original Summary: {recipe_data.get('summary', '')}
Category: {recipe_data.get('category', 'Unknown')}
Cuisine: {recipe_data.get('cuisine', 'Unknown')}
Ingredients: {', '.join(ingredients_list)}
Instructions: {instructions_text}
Level of Effort: {recipe_data.get('difficulty_level', 5)}/10
Prep Time: {prep_time_minutes} minutes
Cook Time: {cook_time_minutes} minutes
Relevance Ratings – Family: {family_score}/10, Single: {single_score}/10, Health: {health_score}/10
Nutrition (per serving): {calories} kcal, {protein} protein, {carbs} carbs, {fat} fat
"""

        # Call OpenAI API to generate the natural language summary
        client = get_openai_client()
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=150,
            temperature=0.3,  # Lower temperature for more consistent output
        )
        
        summary = response.choices[0].message.content.strip()
        if not summary:
            raise ValueError('No summary generated from OpenAI')
        
        logger.info(f"Generated embedding prompt for recipe: {recipe_data.get('title', 'Unknown')}")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating embedding prompt: {e}")
        # Fallback to a simple summary if AI generation fails
        fallback_summary = f"{recipe_data.get('title', 'Recipe')} - {recipe_data.get('cuisine', '')} {recipe_data.get('category', 'dish')} with {', '.join(recipe_data.get('ingredients', []))[:100]}..."
        return fallback_summary

def extract_recipe_data(url: str) -> Optional[Dict[str, Any]]:
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

def extract_json_ld_recipe(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
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

def format_recipe_from_json_ld(recipe_data: dict) -> Dict[str, Any]:
    """Format recipe data from JSON-LD."""
    try:
        title = recipe_data.get('name', 'Unknown Recipe')
        description = recipe_data.get('description', '')
        ingredients = recipe_data.get('recipeIngredient', [])
        instructions = recipe_data.get('recipeInstructions', [])
        
        # Ensure ingredients is a list
        if isinstance(ingredients, str):
            ingredients = [ingredients]
        elif not isinstance(ingredients, list):
            ingredients = []
        
        # Ensure instructions is a list
        if isinstance(instructions, str):
            instructions = [instructions]
        elif not isinstance(instructions, list):
            instructions = []
        
        # Extract text from instruction objects if needed
        formatted_instructions = []
        for instruction in instructions:
            if isinstance(instruction, dict):
                text = instruction.get('text', str(instruction))
                formatted_instructions.append(text)
            else:
                formatted_instructions.append(str(instruction))
        
        return {
            "title": title,
            "summary": description,
            "ingredients": ingredients,
            "instruction_details": formatted_instructions,
            "tools": extract_tools_from_instructions(formatted_instructions)
        }
        
    except Exception as e:
        logger.error(f"Error formatting recipe from JSON-LD: {e}")
        return {
            "title": "Unknown Recipe",
            "summary": "",
            "ingredients": [],
            "instruction_details": []
        }

async def enrich_recipe_with_ai(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich recipe data with AI-generated information using OpenAI."""
    try:
        logger.info(f"Enriching recipe with AI: {recipe_data.get('title', 'Unknown')}")
        
        # Prepare the recipe data for AI analysis
        # Prepare instructions text to avoid f-string backslash issue
        instructions_text = '\n'.join(recipe_data.get('instructions', []))
        
        recipe_text = f"""
Title: {recipe_data.get('title', 'Unknown')}
Ingredients: {', '.join(recipe_data.get('ingredients', []))}
Instructions: {instructions_text}
URL: {recipe_data.get('link', 'No URL')}
"""
        
        # Use the imported prompt
        prompt = RECIPE_ENRICHMENT_PROMPT.format(recipe_text=recipe_text)
        
        # Call OpenAI API with JSON schema
        client = get_openai_client()
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",  # Cost-effective model
            messages=[
                {"role": "system", "content": RECIPE_ENRICHMENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_schema", "json_schema": RECIPE_ENRICHMENT_JSON_SCHEMA},
            temperature=0.3,  # Lower temperature for more consistent results
            max_tokens=500
        )
        
        # Parse the AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Parse the JSON response
        try:
            enriched_info = json.loads(ai_response)
            
            # Merge with original recipe data
            enriched_data = recipe_data.copy()
            enriched_data.update(enriched_info)
            
            logger.info(f"Successfully enriched recipe with AI: {enriched_data.get('title', 'Unknown')}")
            return enriched_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"AI response: {ai_response}")
            # Fall back to basic enrichment
            return _fallback_enrichment(recipe_data)
        
    except Exception as e:
        logger.error(f"Error enriching recipe with AI: {e}")
        # Fall back to basic enrichment
        return _fallback_enrichment(recipe_data)

def _fallback_enrichment(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback enrichment when AI fails."""
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
    enriched_data.setdefault("tags", [])
    enriched_data.setdefault("nutrition_notes", "Nutrition information not available")
    enriched_data.setdefault("cooking_tips", "Follow the recipe instructions carefully")
    
    # Add relevance scores
    enriched_data["relevance"] = {
        "family": 0.8,
        "single": 0.6,
        "health": 0.7
    }
    
    return enriched_data

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

# Tool extraction utilities from scraper service
COOKING_TOOLS = [
    # Cooking appliances
    "slow cooker", "instant pot", "rice cooker", "pressure cooker", "air fryer",
    "food processor", "blender", "stand mixer", "hand mixer", "immersion blender",
    "sous vide", "microwave", "oven", "toaster oven", "broiler", "deep fryer",

    # Cookware
    "skillet", "frying pan", "saucepan", "stockpot", "dutch oven",
    "grill", "griddle", "wok", "sheet pan", "baking dish", "casserole dish",
    "mortar and pestle", "roasting pan", "steamer basket", "colander",

    # Baking-specific tools
    "rolling pin", "pastry brush", "flour sifter", "bench scraper",
    "cookie sheet", "muffin tin", "loaf pan", "cake pan", "springform pan",
    "pie dish", "cooling rack", "dough hook", "piping bag", "measuring cups", "measuring spoons",

    # Utensils & techniques
    "knife", "chef's knife", "paring knife", "chopping", "peeler",
    "whisk", "spatula", "ladle", "tongs", "mixing bowl", "grater", "zester",
    "can opener", "thermometer", "meat thermometer", "kitchen scale"
]

def extract_tools_from_instructions(instructions) -> List[str]:
    """
    Extract cooking tools from recipe instructions.
    
    Args:
        instructions: Recipe instructions (list or string)
        
    Returns:
        List of cooking tools found in the instructions
    """
    found_tools = set()
    
    if isinstance(instructions, list):
        text_array = instructions
    elif isinstance(instructions, str):
        text_array = [instructions]
    else:
        return []
    
    for text in text_array:
        if not text:
            continue
        lower_text = text.lower()
        for tool in COOKING_TOOLS:
            if tool in lower_text:
                found_tools.add(tool)
    
    return list(found_tools) 