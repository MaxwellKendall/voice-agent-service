"""Configuration for MCP server."""

import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for MCP server."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # Database Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://admin:secret@localhost:27017")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # MCP Configuration
    MCP_PROTOCOL_VERSION: str = os.getenv("MCP_PROTOCOL_VERSION", "2024-11-05")
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "Recipe Agent MCP Server")
    MCP_SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        return True
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration."""
        return {
            "mongodb_url": cls.MONGODB_URL,
            "qdrant_url": cls.QDRANT_URL
        }
    
    @classmethod
    def get_server_config(cls) -> dict:
        """Get server configuration."""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "debug": cls.DEBUG
        }
    
    @classmethod
    def get_openai_config(cls) -> dict:
        """Get OpenAI configuration."""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "model": cls.OPENAI_MODEL,
            "embedding_model": cls.OPENAI_EMBEDDING_MODEL
        }

# Global config instance
config = Config() 