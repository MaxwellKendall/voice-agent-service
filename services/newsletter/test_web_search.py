#!/usr/bin/env python3
"""Test script for web search functionality."""

import os
from dotenv import load_dotenv
from app.agent import create_web_search_tool

# Load environment variables
load_dotenv()

def test_web_search():
    """Test the web search tool creation and basic functionality."""
    print("Testing web search tool...")
    
    try:
        # Create the web search tool
        web_search_tool = create_web_search_tool()
        print(f"✅ Web search tool created successfully: {web_search_tool.name}")
        print(f"   Description: {web_search_tool.description}")
        
        # Test with a simple query
        test_query = "latest cooking trends 2024"
        print(f"\nTesting with query: '{test_query}'")
        
        # Handle different tool types
        if hasattr(web_search_tool, 'func'):
            result = web_search_tool.func(test_query)
        else:
            # For DuckDuckGo and other LangChain tools
            result = web_search_tool.run(test_query)
        print(f"✅ Web search result: {result[:200]}...")
        
    except Exception as e:
        print(f"❌ Error testing web search: {e}")
        print("\nTo fix this, you can:")
        print("1. Get a free Tavily API key from https://tavily.com/")
        print("2. Add TAVILY_API_KEY=your_key to your .env file")
        print("3. Or get a SerpAPI key from https://serpapi.com/")
        print("4. Or the tool will fall back to DuckDuckGo (no API key needed)")

if __name__ == "__main__":
    test_web_search() 