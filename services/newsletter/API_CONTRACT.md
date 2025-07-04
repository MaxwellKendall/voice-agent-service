# AI Recipe Agent API Contract

**Base URL**: `http://localhost:8000`  
**Content-Type**: `application/json`

## Overview

The AI Recipe Agent API is designed to help users explore recipes and cooking topics while building content for newsletters. The chat endpoint guides conversations toward creating comprehensive newsletter content.

## Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/` | Health check | None | `{"status": "healthy", "version": "1.0.0", "timestamp": "..."}` |
| `POST` | `/chat` | Chat with AI agent (newsletter-focused) | `{"message": "string", "chat_history": [...]}` | `{"response": "string", "recipes": [...], "tool_calls": [...]}` |
| `GET` | `/tools` | List available tools | None | `{"tools": [...]}` |

## Request/Response Details

### POST /chat

**Request:**
```json
{
  "message": "What are some easy Mexican recipes?",
  "chat_history": [
    {"role": "user", "content": "I want Mexican food"},
    {"role": "assistant", "content": "I can help you find Mexican recipes!"}
  ]
}
```

**Response:**
```json
{
  "response": "I found several delicious Mexican recipes for you! Here are some easy options:\n\n1. **Chicken Enchiladas** - A classic Mexican dish...",
  "recipes": [
    {
      "id": "recipe_001",
      "title": "Easy Chicken Enchiladas", 
      "summary": "Classic Mexican enchiladas with tender chicken",
      "url": "https://example.com/recipes/chicken-enchiladas",
      "score": 0.92
    }
  ],
  "tool_calls": [
    {
      "tool_name": "search_recipes",
      "arguments": {"query": "easy Mexican recipes"},
      "result": "Found 5 recipes matching criteria"
    }
  ]
}
```

### GET /tools

**Response:**
```json
{
  "tools": [
    {
      "name": "search_recipes",
      "description": "Search for recipes using a natural language query in our database",
      "args_schema": "query: str"
    },
    {
      "name": "get_similar_recipes",
      "description": "Find recipes similar to a specific recipe by ID in our database", 
      "args_schema": "recipe_id: str"
    },
    {
      "name": "find_similar_recipes_from_url",
      "description": "Find recipes similar to a recipe from a web URL by extracting its content and searching our database",
      "args_schema": "recipe_url: str"
    },
    {
      "name": "search_recipes_with_web_context",
      "description": "Search for recipes and enhance results with current web search context",
      "args_schema": "query: str"
    }
  ]
}
```

## Example Queries

| Query Type | Example | Expected Response |
|------------|---------|-------------------|
| Recipe Search | "Find vegetarian pasta dishes" | List of vegetarian pasta recipes |
| Similar Recipes | "What's similar to this beef stew?" | Similar recipes with scores |
| Web Recipe Similarity | "Find recipes similar to this: https://example.com/recipe" | Similar recipes based on web content |
| Enhanced Search | "Show me current trends in keto desserts" | Recipes with web context and trends |
| Cooking Advice | "How do I substitute buttermilk?" | Cooking tips and substitutions |
| Dietary Restrictions | "Show me gluten-free desserts" | Filtered recipe recommendations |

## Newsletter Generation

The chat endpoint is designed to build newsletter content through conversation. The AI agent:

- **Guides conversations** toward diverse recipe topics
- **Explores cooking trends** and current information
- **Gathers multiple recipes** and cooking tips
- **Builds comprehensive content** suitable for newsletter format
- **Uses web search** to provide current trends and insights

## Error Responses

| Status | Description | Response Format |
|--------|-------------|-----------------|
| `200` | Success | Normal response body |
| `422` | Validation Error | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| `500` | Server Error | `{"detail": "Internal server error: ..."}` |

## Quick Examples

**Health Check:**
```bash
curl http://localhost:8000/
```

**Basic Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are some easy Mexican recipes?", "chat_history": []}'
```

**List Tools:**
```bash
curl http://localhost:8000/tools
``` 