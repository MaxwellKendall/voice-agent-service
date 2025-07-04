#!/usr/bin/env python3
"""Example usage of the AI Recipe Agent."""

import asyncio
import json
from typing import List, Dict, Any

# Add the parent directory to the path so we can import app modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.agent import process_query
from app.tools import search_recipes, get_similar_recipes

def example_recipe_search():
    """Example of using the search_recipes tool directly."""
    print("🔍 Example: Recipe Search")
    print("-" * 40)
    
    try:
        # Search for Mexican recipes
        recipes = search_recipes("easy Mexican recipes")
        
        if recipes:
            print(f"Found {len(recipes)} recipes:")
            for i, recipe in enumerate(recipes, 1):
                print(f"{i}. {recipe['title']}")
                print(f"   Summary: {recipe['summary']}")
                print(f"   URL: {recipe['url']}")
                print(f"   Score: {recipe.get('score', 'N/A')}")
                print()
        else:
            print("No recipes found. Make sure your vector database has some recipe data.")
            
    except Exception as e:
        print(f"Error during recipe search: {e}")

def example_similar_recipes():
    """Example of using the get_similar_recipes tool directly."""
    print("🔄 Example: Similar Recipes")
    print("-" * 40)
    
    try:
        # First, search for a recipe to get an ID
        recipes = search_recipes("chili recipe")
        
        if recipes:
            recipe_id = recipes[0]['id']
            print(f"Finding recipes similar to: {recipes[0]['title']}")
            
            # Get similar recipes
            similar = get_similar_recipes(recipe_id)
            
            if similar:
                print(f"Found {len(similar)} similar recipes:")
                for i, recipe in enumerate(similar, 1):
                    print(f"{i}. {recipe['title']}")
                    print(f"   Summary: {recipe['summary']}")
                    print(f"   Similarity Score: {recipe.get('score', 'N/A')}")
                    print()
            else:
                print("No similar recipes found.")
        else:
            print("No base recipe found for similarity search.")
            
    except Exception as e:
        print(f"Error during similar recipe search: {e}")

def example_agent_chat():
    """Example of using the AI agent for natural language queries."""
    print("🤖 Example: AI Agent Chat")
    print("-" * 40)
    
    # Example queries to test
    queries = [
        "What are some easy Mexican recipes?",
        "What's similar to turkey chili?",
        "Find vegetarian pasta dishes",
        "Show me quick breakfast recipes",
        "What are the health benefits of quinoa?"
    ]
    
    for query in queries:
        print(f"\n💬 Query: {query}")
        print("-" * 30)
        
        try:
            response = process_query(query)
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def example_with_chat_history():
    """Example of using the agent with chat history."""
    print("💬 Example: Chat with History")
    print("-" * 40)
    
    # Simulate a conversation
    chat_history = [
        {"role": "user", "content": "Hello, I'm looking for dinner ideas"},
        {"role": "assistant", "content": "Hi! I'd be happy to help you find dinner ideas. What type of cuisine are you interested in?"}
    ]
    
    follow_up = "Actually, I'm in the mood for something spicy"
    
    print(f"💬 Follow-up: {follow_up}")
    print("-" * 30)
    
    try:
        response = process_query(follow_up, chat_history)
        print(f"🤖 Response: {response}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all examples."""
    print("🍳 AI Recipe Agent Examples")
    print("=" * 50)
    
    # Run examples
    example_recipe_search()
    example_similar_recipes()
    example_agent_chat()
    example_with_chat_history()
    
    print("\n" + "=" * 50)
    print("✨ Examples completed!")
    print("\nTo run the full API server:")
    print("python main.py")
    print("\nThen visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 