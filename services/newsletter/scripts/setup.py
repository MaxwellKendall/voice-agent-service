#!/usr/bin/env python3
"""Setup script for the AI Recipe Agent project."""

import os
import sys
from pathlib import Path

# Add the project root to Python path so we can import app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please copy env.example to .env and fill in your API keys")
        return False
    
    with open(env_file) as f:
        content = f.read()
    
    required_vars = ["OPENAI_API_KEY", "VECTOR_DB_URL"]
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=your_" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or unconfigured environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file configured")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import fastapi
        import langchain
        import qdrant_client
        import pydantic
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def test_vector_store_connection():
    """Test connection to Qdrant vector store."""
    try:
        from app.config import get_vector_db_url, get_vector_db_api_key
        from app.vector_store import RecipeVectorStore
        
        url = get_vector_db_url()
        api_key = get_vector_db_api_key()
        
        store = RecipeVectorStore(url=url, api_key=api_key)
        print("✅ Vector store connection successful")
        return True
    except Exception as e:
        print(f"❌ Vector store connection failed: {e}")
        return False

def test_openai_connection():
    """Test OpenAI API connection."""
    try:
        from app.config import get_openai_api_key
        from langchain_openai import OpenAIEmbeddings
        
        api_key = get_openai_api_key()
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        
        # Test with a simple embedding
        test_vector = embeddings.embed_query("test")
        if len(test_vector) > 0:
            print("✅ OpenAI API connection successful")
            return True
        else:
            print("❌ OpenAI API returned empty response")
            return False
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def main():
    """Run all setup checks."""
    print("🔧 AI Recipe Agent Setup Check")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment Variables", check_env_file),
        ("Dependencies", check_dependencies),
        ("Vector Store Connection", test_vector_store_connection),
        ("OpenAI API Connection", test_openai_connection),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ Error during {name} check: {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! You're ready to run the application.")
        print("Run: python main.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above before running the application.")
        sys.exit(1)

if __name__ == "__main__":
    main() 