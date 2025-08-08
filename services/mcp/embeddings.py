"""OpenAI embeddings for recipe similarity."""

import logging
import sys
import os
from typing import List
from openai import OpenAI

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import config
except ImportError:
    # Try relative imports if running as module
    from .config import config

logger = logging.getLogger(__name__)

_embeddings_client: OpenAI = None

def get_embeddings() -> OpenAI:
    """Get or create OpenAI embeddings client."""
    global _embeddings_client
    if _embeddings_client is None:
        _embeddings_client = OpenAI(api_key=config.OPENAI_API_KEY)
        logger.info("OpenAI embeddings client initialized")
    return _embeddings_client

def embed_query(text: str) -> List[float]:
    """Generate embeddings for a text query."""
    try:
        client = get_embeddings()
        response = client.embeddings.create(
            model=config.OPENAI_EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise 