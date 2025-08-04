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
async def extract_and_store_recipe(url: str) -> Dict[str, Any]:
    """
    Extract recipe content from a URL, enrich with AI, store in MongoDB, and add to vector database.
    
    Complete workflow:
    1. Scrape recipe data from JSON-LD
    2. Enrich with AI model
    3. Store in MongoDB (recipes database, parsed_recipes collection)
    4. Generate embeddings
    5. Add to vector store
    
    Args:
        url: The URL of the recipe to extract and store
        
    Returns:
        A dictionary with the recipe ID, title, and status of the operation
    """
    try:
        logger.info(f"Starting complete recipe extraction workflow for URL: {url}")
        
        # Step 1: Extract recipe content from the URL
        recipe_content = extract_recipe_content(url)
        
        if recipe_content.startswith("Error:"):
            return {
                "success": False,
                "error": recipe_content,
                "url": url
            }
        
        # Step 2: Parse the extracted content to get structured recipe data
        recipe_data = parse_recipe_content(recipe_content, url)
        
        # Step 3: Enrich recipe data with AI
        try:
            enriched_data = await enrich_recipe_with_ai(recipe_data)
        except Exception as e:
            logger.warning(f"AI enrichment failed, using original data: {e}")
            enriched_data = recipe_data
        
        # Step 4: Store recipe in MongoDB
        try:
            from app.mongo import get_recipe_service
            recipe_service = get_recipe_service()
            
            # Check if recipe already exists
            existing_recipe = await recipe_service.get_recipe_by_url(url)
            if existing_recipe:
                logger.info(f"Recipe already exists in database: {existing_recipe['_id']}")
                mongo_id = existing_recipe['_id']
            else:
                # Add recipe to MongoDB
                mongo_id = await recipe_service.add_recipe(enriched_data)
                logger.info(f"Added recipe to MongoDB with ID: {mongo_id}")
        except Exception as e:
            logger.error(f"Failed to store recipe in MongoDB: {e}")
            # Continue with vector store even if MongoDB fails
            mongo_id = None
        
        # Step 5: Generate embeddings for the recipe summary
        embeddings = get_embeddings()
        recipe_vector = embeddings.embed_query(enriched_data.get("summary", recipe_content))
        
        # Step 6: Add recipe to vector store
        vector_store = get_vector_store()
        
        # Update enriched data with MongoDB ID
        if mongo_id:
            enriched_data['mongo_id'] = mongo_id
        
        vector_id = vector_store.add_recipe(enriched_data, recipe_vector)
        
        logger.info(f"Successfully completed recipe extraction workflow")
        logger.info(f"  - MongoDB ID: {mongo_id}")
        logger.info(f"  - Vector Store ID: {vector_id}")
        logger.info(f"  - URL: {url}")
        
        return {
            "success": True,
            "mongo_id": mongo_id,
            "vector_id": vector_id,
            "title": enriched_data.get("title", "Unknown"),
            "url": url,
            "summary": enriched_data.get("summary", "")[:100] + "..." if len(enriched_data.get("summary", "")) > 100 else enriched_data.get("summary", ""),
            "cuisine": enriched_data.get("cuisine", ""),
            "category": enriched_data.get("category", ""),
            "difficulty_level": enriched_data.get("difficulty_level", "Unknown"),
            "relevance": enriched_data.get("relevance", {})
        }
        
    except Exception as e:
        logger.error(f"Error in extract_and_store_recipe: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        }

def parse_recipe_content(recipe_content: str, url: str) -> Dict[str, Any]:
    """
    Parse extracted recipe content into structured data conforming to RecipeVector schema.
    
    Args:
        recipe_content: The extracted recipe content
        url: The source URL
        
    Returns:
        Structured recipe data dictionary
    """
    try:
        import json
        from datetime import datetime
        
        # Try to parse as JSON-LD first
        try:
            recipe_data = json.loads(recipe_content)
            if isinstance(recipe_data, dict) and recipe_data.get("@type") == "Recipe":
                # Extract tools from recipe instructions
                tools = extract_tools_from_recipe(recipe_data)
                
                # Extract keywords from title and description
                keywords = extract_keywords_from_recipe(recipe_data)
                
                return {
                    "title": recipe_data.get("name", "Unknown Recipe"),
                    "summary": recipe_data.get("description", ""),
                    "link": url,
                    "source": extract_domain(url),
                    "ingredients": [ingredient.get("name", "") for ingredient in recipe_data.get("recipeIngredient", [])],
                    "prep_time": recipe_data.get("prepTime", ""),
                    "cook_time": recipe_data.get("cookTime", ""),
                    "servings": recipe_data.get("recipeYield", ""),
                    "cuisine": recipe_data.get("recipeCuisine", ""),
                    "category": recipe_data.get("recipeCategory", ""),
                    "rating": recipe_data.get("aggregateRating", {}).get("ratingValue", ""),
                    "rating_count": recipe_data.get("aggregateRating", {}).get("reviewCount", ""),
                    "image_url": recipe_data.get("image", {}).get("url", "") if isinstance(recipe_data.get("image"), dict) else recipe_data.get("image", ""),
                    "tools": tools,
                    "keywords": keywords,
                    "created_at": datetime.now().isoformat()
                }
        except (json.JSONDecodeError, KeyError):
            pass
        
        # Fallback: create basic structure from text content
        return {
            "title": "Extracted Recipe",
            "summary": recipe_content[:500] + "..." if len(recipe_content) > 500 else recipe_content,
            "link": url,
            "source": extract_domain(url),
            "ingredients": [],
            "prep_time": "",
            "cook_time": "",
            "servings": "",
            "cuisine": "",
            "category": "",
            "rating": "",
            "rating_count": "",
            "image_url": "",
            "tools": [],
            "keywords": [],
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error parsing recipe content: {e}")
        return {
            "title": "Extracted Recipe",
            "summary": recipe_content,
            "link": url,
            "source": extract_domain(url),
            "tools": [],
            "keywords": [],
            "created_at": datetime.now().isoformat()
        }

def extract_tools_from_recipe(recipe_data: dict) -> list:
    """Extract cooking tools from recipe data."""
    tools = []
    common_tools = [
        "oven", "stovetop", "microwave", "blender", "food processor", 
        "mixer", "grill", "slow cooker", "instant pot", "air fryer",
        "sheet pan", "baking dish", "skillet", "pot", "pan", "bowl",
        "knife", "cutting board", "measuring cups", "spatula", "whisk"
    ]
    
    # Check recipe instructions for tools
    instructions = recipe_data.get("recipeInstructions", [])
    if isinstance(instructions, list):
        for instruction in instructions:
            if isinstance(instruction, dict):
                text = instruction.get("text", "")
            else:
                text = str(instruction)
            
            text_lower = text.lower()
            for tool in common_tools:
                if tool in text_lower:
                    tools.append(tool)
    
    return list(set(tools))  # Remove duplicates

def extract_keywords_from_recipe(recipe_data: dict) -> list:
    """Extract keywords from recipe title and description."""
    keywords = []
    
    # Extract from title
    title = recipe_data.get("name", "")
    if title:
        keywords.extend(title.lower().split())
    
    # Extract from description
    description = recipe_data.get("description", "")
    if description:
        keywords.extend(description.lower().split())
    
    # Filter out common words and keep meaningful keywords
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"}
    
    filtered_keywords = [word for word in keywords if word not in stop_words and len(word) > 2]
    
    return list(set(filtered_keywords))  # Remove duplicates

async def enrich_recipe_with_ai(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich recipe data using a cheap AI model.
    
    Args:
        recipe_data: The parsed recipe data
        
    Returns:
        Enriched recipe data
    """
    try:
        from app.config import get_openai_api_key
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=get_openai_api_key())
        
        # Create a prompt for recipe enrichment
        prompt = f"""
        Please enrich the following recipe data with additional insights. 
        Focus on improving the summary, extracting better keywords, and categorizing the recipe.
        
        Recipe Title: {recipe_data.get('title', 'Unknown')}
        Original Summary: {recipe_data.get('summary', '')}
        Ingredients: {recipe_data.get('ingredients', [])}
        Prep Time: {recipe_data.get('prep_time', '')}
        Cook Time: {recipe_data.get('cook_time', '')}
        Servings: {recipe_data.get('servings', '')}
        Cuisine: {recipe_data.get('cuisine', '')}
        Category: {recipe_data.get('category', '')}
        
        Please provide the following in JSON format:
        1. An improved, engaging summary (2-3 sentences)
        2. Enhanced keywords (focus on ingredients, techniques, dietary info)
        3. Better cuisine classification if needed
        4. Better category classification if needed
        5. Estimated difficulty level (1-5, where 1=very easy, 5=very hard)
        6. Suggested cooking tools needed
        7. Health score (0-1, where 1=very healthy)
        8. Family-friendliness score (0-1, where 1=very family-friendly)
        9. Persona relevance scores (1-10 scale):
           - family: How relevant for families with children (1=not suitable, 10=perfect for families)
           - single: How relevant for single people/couples (1=not suitable, 10=perfect for singles)
           - health: How healthy/nutritious the recipe is (1=unhealthy, 10=very healthy)
        
        Return only valid JSON with these fields: summary, keywords, cuisine, category, difficulty_level, tools, health_score, family_score, relevance
        """
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using cheaper model
            messages=[
                {"role": "system", "content": "You are a recipe analysis expert. Provide concise, accurate enrichments in JSON format only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent results
            max_tokens=500
        )
        
        # Parse the AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        import json
        import re
        
        # Find JSON in the response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            ai_data = json.loads(json_match.group())
        else:
            # Fallback: try to parse the entire response
            ai_data = json.loads(ai_response)
        
        # Merge AI enrichments with original data
        enriched_data = {**recipe_data}
        
        if 'summary' in ai_data:
            enriched_data['summary'] = ai_data['summary']
        if 'keywords' in ai_data:
            enriched_data['keywords'] = ai_data['keywords']
        if 'cuisine' in ai_data:
            enriched_data['cuisine'] = ai_data['cuisine']
        if 'category' in ai_data:
            enriched_data['category'] = ai_data['category']
        if 'difficulty_level' in ai_data:
            enriched_data['difficulty_level'] = ai_data['difficulty_level']
        if 'tools' in ai_data:
            enriched_data['tools'] = ai_data['tools']
        if 'health_score' in ai_data:
            enriched_data['health_score'] = ai_data['health_score']
        if 'family_score' in ai_data:
            enriched_data['family_score'] = ai_data['family_score']
        if 'relevance' in ai_data:
            enriched_data['relevance'] = ai_data['relevance']
        
        logger.info(f"Successfully enriched recipe: {recipe_data.get('title', 'Unknown')}")
        return enriched_data
        
    except Exception as e:
        logger.error(f"Error enriching recipe with AI: {e}")
        # Return original data if enrichment fails
        return recipe_data

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return "unknown"

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
        search_recipes_with_web_context,
        extract_and_store_recipe
    ] 