"""Configuration settings for the AI agent application."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return key

def get_vector_db_api_key() -> Optional[str]:
    """Get Qdrant API key from environment."""
    return os.getenv("VECTOR_DB_API_KEY")

def get_vector_db_url() -> str:
    """Get Qdrant URL from environment."""
    url = os.getenv("VECTOR_DB_URL")
    if not url:
        raise ValueError("VECTOR_DB_URL environment variable is required")
    return url

def get_tavily_api_key() -> Optional[str]:
    """Get Tavily API key from environment."""
    return os.getenv("TAVILY_API_KEY")

def get_serpapi_key() -> Optional[str]:
    """Get SerpAPI key from environment."""
    return os.getenv("SERPAPI_API_KEY")

# Application settings
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000")) 