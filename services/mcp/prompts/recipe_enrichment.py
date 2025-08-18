"""Recipe enrichment prompts for AI analysis."""

RECIPE_ENRICHMENT_PROMPT = """
You are a culinary expert. Analyze this recipe and provide enriched information in JSON format.

Recipe:
{recipe_text}

Please provide the following information in JSON format:
1. cuisine: The type of cuisine (e.g., "Italian", "Mexican", "Asian", "American", "Mediterranean")
2. category: The meal category (e.g., "Main Dish", "Appetizer", "Dessert", "Soup", "Salad", "Breakfast")
3. difficulty_level: A number from 1-5 (1=easy, 5=expert)
4. servings: Number of people this recipe serves
5. prep_time: Estimated prep time in minutes
6. cook_time: Estimated cooking time in minutes
7. total_time: Total time (prep + cook) in minutes
8. rating: A realistic rating from 1.0 to 5.0
9. rating_count: Number of ratings (realistic number)
10. relevance: Object with scores from 0.0 to 1.0 for:
    - family: How suitable for families with children
    - single: How suitable for single people
    - health: How healthy this recipe is
11. tags: Array of relevant tags (e.g., ["vegetarian", "quick", "budget-friendly"])
12. nutrition_notes: Brief nutrition information
13. cooking_tips: 1-2 helpful cooking tips

Return ONLY valid JSON, no other text.
"""

RECIPE_ENRICHMENT_SYSTEM_PROMPT = "You are a culinary expert. Always respond with valid JSON only."

RECIPE_ENRICHMENT_JSON_SCHEMA = {
    "name": "recipe_enrichment",
    "description": "Enriched recipe information including cuisine, category, difficulty, timing, ratings, and relevance scores",
    "schema": {
        "type": "object",
        "properties": {
            "cuisine": {
                "type": "string",
                "description": "The type of cuisine (e.g., Italian, Mexican, Asian, American, Mediterranean)"
            },
            "category": {
                "type": "string",
                "description": "The meal category (e.g., Main Dish, Appetizer, Dessert, Soup, Salad, Breakfast)"
            },
            "difficulty_level": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Difficulty level from 1 (easy) to 5 (expert)"
            },
            "servings": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of people this recipe serves"
            },
            "prep_time": {
                "type": "string",
                "description": "Estimated prep time (e.g., '30 minutes')"
            },
            "cook_time": {
                "type": "string",
                "description": "Estimated cooking time (e.g., '45 minutes')"
            },
            "total_time": {
                "type": "string",
                "description": "Total time including prep and cook (e.g., '75 minutes')"
            },
            "rating": {
                "type": "number",
                "minimum": 1.0,
                "maximum": 5.0,
                "description": "A realistic rating from 1.0 to 5.0"
            },
            "rating_count": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of ratings (realistic number)"
            },
            "relevance": {
                "type": "object",
                "properties": {
                    "family": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "How suitable for families with children"
                    },
                    "single": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "How suitable for single people"
                    },
                    "health": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "How healthy this recipe is"
                    }
                },
                "required": ["family", "single", "health"],
                "additionalProperties": False
            },
            "tags": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Array of relevant tags (e.g., ['vegetarian', 'quick', 'budget-friendly'])"
            },
            "nutrition_notes": {
                "type": "string",
                "description": "Brief nutrition information"
            },
            "cooking_tips": {
                "type": "string",
                "description": "1-2 helpful cooking tips"
            }
        },
        "required": [
            "cuisine", "category", "difficulty_level", "servings", 
            "prep_time", "cook_time", "total_time", "rating", 
            "rating_count", "relevance", "tags", "nutrition_notes", "cooking_tips"
        ],
        "additionalProperties": False
    },
    "strict": True
}
