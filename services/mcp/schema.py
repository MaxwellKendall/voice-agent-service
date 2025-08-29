"""
Centralized Recipe Schema Definition

This module provides a centralized schema definition for recipe objects across the application.
It uses Pydantic for runtime validation and handles snake_case/camelCase conversion.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator
import re


class Nutrients(BaseModel):
    """Nutritional information for a recipe."""
    serving_size: str = Field(..., description="Serving size description")
    calories: str = Field(..., description="Calories per serving")
    carbohydrate_content: Optional[str] = Field(..., description="Carbohydrates per serving")
    protein_content: Optional[str] = Field(..., description="Protein per serving")
    fat_content: Optional[str] = Field(..., description="Fat per serving")
    cholesterol_content: Optional[str] = Field(..., description="Cholesterol per serving")
    sodium_content: Optional[str] = Field(..., description="Sodium per serving")
    fiber_content: Optional[str] = Field(..., description="Fiber per serving")
    sugar_content: Optional[str] = Field(..., description="Sugar per serving")

    class Config:
        # Allow camelCase field names for API compatibility
        alias_generator = lambda string: re.sub(r'_([a-z])', lambda m: m.group(1).upper(), string)
        validate_by_name = True


class Relevance(BaseModel):
    """Relevance scores for different personas."""
    family: float = Field(..., ge=0, le=10, description="Relevance score for family cooking (0-10)")
    single: float = Field(..., ge=0, le=10, description="Relevance score for single person cooking (0-10)")
    health: float = Field(..., ge=0, le=10, description="Relevance score for health-conscious cooking (0-10)")

    class Config:
        alias_generator = lambda string: re.sub(r'_([a-z])', lambda m: m.group(1).upper(), string)
        allow_population_by_field_name = True

class Recipe(BaseModel):
    """Main recipe schema definition."""
    
    # Required fields
    title: str = Field(..., min_length=1, max_length=200, description="Recipe title (potentially modified by AI enrichment process)")
    original_title: Optional[str] = Field(..., min_length=1, max_length=200, description="Original recipe title from source")
    ingredients: str = Field(..., description="Ingredients list as string")
    instruction_details: List[str] = Field(..., min_items=1, description="Step-by-step cooking instructions")
    servings: List[str] = Field(..., min_items=1, description="Number of servings")
    prep_time: str = Field(..., description="Preparation time")
    cook_time: str = Field(..., description="Cooking time")
    cuisine: str = Field(..., description="Cuisine type")
    category: str = Field(..., description="Recipe category")
    rating: float = Field(..., ge=0, le=5, description="Recipe rating (0-5)")
    rating_count: int = Field(..., ge=0, description="Number of ratings")
    tools: List[str] = Field(default_factory=list, description="Required cooking tools")
    image_url: str = Field(..., description="Recipe image URL")
    relevance: Relevance = Field(..., description="Relevance scores for different personas")
    link: str = Field(..., description="Original recipe link")
    source: str = Field(..., description="Recipe source")
    original_summary: Optional[str] = Field(..., description="Original summary from source")
    nutrients: Nutrients = Field(..., description="Nutritional information")
            
    class Config:
        # Allow camelCase field names for API compatibility
        alias_generator = lambda string: re.sub(r'_([a-z])', lambda m: m.group(1).upper(), string)
        validate_by_name = True
        # Extra fields are allowed to handle legacy data
        extra = "allow"
    
    @field_validator('title', 'original_title')
    @classmethod
    def validate_title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @field_validator('ingredients')
    @classmethod
    def validate_ingredients_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Ingredients cannot be empty')
        return v.strip()
    
    @field_validator('instruction_details')
    @classmethod
    def validate_instructions_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Instructions cannot be empty')
        # Remove empty instructions
        return [instruction.strip() for instruction in v if instruction.strip()]
    
    @field_validator('servings')
    @classmethod
    def validate_servings_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Servings cannot be empty')
        return v
    
    @model_validator(mode='after')
    def validate_total_time_consistency(self):
        """Validate that timing information is consistent."""
        prep_time = self.prep_time
        cook_time = self.cook_time
        
        if prep_time and cook_time:
            # Basic validation that times are not negative
            try:
                prep_minutes = self._parse_time_to_minutes(prep_time)
                cook_minutes = self._parse_time_to_minutes(cook_time)
                if prep_minutes < 0 or cook_minutes < 0:
                    raise ValueError('Time values cannot be negative')
            except ValueError:
                # If we can't parse the time, that's okay - just skip validation
                pass
        
        return self
    
    @staticmethod
    def _parse_time_to_minutes(time_str: str) -> int:
        """Parse time string to minutes."""
        if not time_str:
            return 0
        
        # Handle "PT5M" format (ISO 8601 duration)
        pt_match = re.match(r'PT(\d+)M', time_str)
        if pt_match:
            return int(pt_match.group(1))
        
        # Handle "30 minutes" format
        minutes_match = re.match(r'(\d+)', time_str)
        if minutes_match:
            return int(minutes_match.group(1))
        
        # If we can't parse it, return 0
        return 0

class EnrichedRecipe(Recipe):
    """Recipes enriched with additional information."""
    summary: Optional[str] = Field(..., description="Recipe summary")
    title: Optional[str] = Field(..., min_length=1, max_length=200, description="Recipe title")
    level_of_effort: Optional[int] = Field(..., ge=1, le=10, description="Difficulty level (1-10)")
    qualified: Optional[bool] = Field(..., description="Whether recipe meets quality standards")
    keywords: Optional[str] = Field(..., description="Recipe keywords")
    vector_embedded: Optional[bool] = Field(False, description="Whether recipe has been embedded in vector database")
    vector_id: Optional[str] = Field(None, description="Vector database entry ID")
    embedding_prompt: Optional[str] = Field(None, description="Natural language summary for embeddings")
    # MongoDB ID (optional for creation, required for retrieval)
    mongo_id: Optional[str] = Field(None, alias="_id", description="MongoDB ObjectId")

# Runtime validation functions
def validate_recipe(data: Dict[str, Any]) -> Recipe:
    """
    Validate recipe data and return a Recipe object.
    
    Args:
        data: Dictionary containing recipe data (can be camelCase or snake_case)
        
    Returns:
        Recipe: Validated recipe object
        
    Raises:
        ValidationError: If data doesn't match the schema
    """
    try:
        return Recipe(**data)
    except Exception as e:
        raise ValueError(f"Recipe validation failed: {str(e)}")

def recipe_to_dict(recipe: Recipe, use_camel_case: bool = True) -> Dict[str, Any]:
    """
    Convert a Recipe object to a dictionary.
    
    Args:
        recipe: Recipe object to convert
        use_camel_case: If True, use camelCase keys; if False, use snake_case keys
        
    Returns:
        Dict[str, Any]: Recipe data as dictionary
    """
    if use_camel_case:
        return recipe.model_dump(by_alias=True)
    else:
        return recipe.model_dump(by_alias=False)

def dict_to_recipe(data: Dict[str, Any]) -> Recipe:
    """
    Convert a dictionary to a Recipe object.
    
    Args:
        data: Dictionary containing recipe data (can be camelCase or snake_case)
        
    Returns:
        Recipe: Recipe object
    """
    return validate_recipe(data)

# Utility functions for field conversion
def to_snake_case(camel_case_str: str) -> str:
    """Convert camelCase string to snake_case."""
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', camel_case_str).lower()


def to_camel_case(snake_case_str: str) -> str:
    """Convert snake_case string to camelCase."""
    components = snake_case_str.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def convert_dict_keys(data: Dict[str, Any], to_camel: bool = True) -> Dict[str, Any]:
    """
    Convert dictionary keys between snake_case and camelCase.
    
    Args:
        data: Dictionary to convert
        to_camel: If True, convert to camelCase; if False, convert to snake_case
        
    Returns:
        Dict[str, Any]: Dictionary with converted keys
    """
    result = {}
    for key, value in data.items():
        if to_camel:
            new_key = to_camel_case(key)
        else:
            new_key = to_snake_case(key)
        
        if isinstance(value, dict):
            result[new_key] = convert_dict_keys(value, to_camel)
        elif isinstance(value, list):
            result[new_key] = [
                convert_dict_keys(item, to_camel) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[new_key] = value
    
    return result


# Export the main classes and functions
__all__ = [
    'Recipe',
    'EnrichedRecipe',
    'Nutrients',
    'Relevance',
    'validate_recipe',
    'recipe_to_dict',
    'dict_to_recipe',
    'to_snake_case',
    'to_camel_case',
    'convert_dict_keys'
]
