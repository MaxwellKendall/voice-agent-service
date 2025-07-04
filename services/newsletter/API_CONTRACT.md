# AI Recipe Agent API Contract

**Base URL**: `http://localhost:8000`  
**Content-Type**: `application/json`

## Overview

The AI Recipe Agent API is designed to help users explore recipes and cooking topics while building content for newsletters. The chat endpoint guides conversations toward creating comprehensive newsletter content, with persistent chat history stored in MongoDB.

## Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| `GET` | `/` | Health check | None | `{"status": "healthy", "version": "1.0.0", "timestamp": "..."}` |
| `POST` | `/chat` | Chat with AI agent (newsletter-focused) | `{"message": "string", "chat_id": "string"}` | `{"response": "string", "chat_id": "string", "recipes": [...], "tool_calls": [...]}` |
| `GET` | `/chats` | Get all chat sessions | None | `{"chats": [...]}` |
| `GET` | `/chats/{chat_id}` | Get specific chat with messages | None | `{"chat": {...}, "messages": [...]}` |
| `DELETE` | `/chats/{chat_id}` | Delete a chat session | None | `{"message": "Chat deleted successfully"}` |
| `GET` | `/tools` | List available tools | None | `{"tools": [...]}` |

## Request/Response Details

### POST /chat

**Request:**
```json
{
  "message": "What are some easy Mexican recipes?",
  "chat_id": "507f1f77bcf86cd799439011"
}
```

**Response:**
```json
{
  "response": "I found several delicious Mexican recipes for you! Here are some easy options:\n\n1. **Chicken Enchiladas** - A classic Mexican dish...",
  "chat_id": "507f1f77bcf86cd799439011",
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

**Notes:**
- If `chat_id` is `null` or not provided, a new chat session will be created
- The response includes the `chat_id` (new or existing) for client reference
- All messages are automatically persisted to MongoDB

### GET /chats

**Response:**
```json
{
  "chats": [
    {
      "id": "507f1f77bcf86cd799439011",
      "title": "Mexican Cooking Session",
      "created_at": "2024-01-15T10:30:00.000Z",
      "updated_at": "2024-01-15T11:45:00.000Z",
      "message_count": 8
    },
    {
      "id": "507f1f77bcf86cd799439012",
      "title": "Italian Pasta Recipes",
      "created_at": "2024-01-14T09:15:00.000Z",
      "updated_at": "2024-01-14T10:20:00.000Z",
      "message_count": 6
    }
  ]
}
```

### GET /chats/{chat_id}

**Response:**
```json
{
  "chat": {
    "id": "507f1f77bcf86cd799439011",
    "title": "Mexican Cooking Session",
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T11:45:00.000Z",
    "message_count": 8
  },
  "messages": [
    {
      "id": "507f1f77bcf86cd799439021",
      "chat_id": "507f1f77bcf86cd799439011",
      "role": "user",
      "content": "What are some easy Mexican recipes?",
      "created_at": "2024-01-15T10:30:00.000Z"
    },
    {
      "id": "507f1f77bcf86cd799439022",
      "chat_id": "507f1f77bcf86cd799439011",
      "role": "assistant",
      "content": "I found several delicious Mexican recipes for you!...",
      "created_at": "2024-01-15T10:30:05.000Z"
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
- **Persists all conversations** in MongoDB for continuity

## Chat Management

The API provides comprehensive chat management:

- **Automatic chat creation** when starting new conversations
- **Persistent chat history** stored in MongoDB
- **Chat listing** to see all previous sessions
- **Individual chat retrieval** with full message history
- **Chat deletion** to clean up old conversations

## Error Responses

| Status | Description | Response Format |
|--------|-------------|-----------------|
| `200` | Success | Normal response body |
| `404` | Chat Not Found | `{"detail": "Chat not found"}` |
| `422` | Validation Error | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| `500` | Server Error | `{"detail": "Internal server error: ..."}` |

## Quick Examples

**Health Check:**
```bash
curl http://localhost:8000/
```

**Start New Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are some easy Mexican recipes?"}'
```

**Continue Existing Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me more about enchiladas",
    "chat_id": "507f1f77bcf86cd799439011"
  }'
```

**Get All Chats:**
```bash
curl http://localhost:8000/chats
```

**Get Specific Chat:**
```bash
curl http://localhost:8000/chats/507f1f77bcf86cd799439011
```

**Delete Chat:**
```bash
curl -X DELETE http://localhost:8000/chats/507f1f77bcf86cd799439011
```

**List Tools:**
```bash
curl http://localhost:8000/tools
```

## Environment Variables

Required environment variables (set in `.env` file):

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here
VECTOR_DB_URL=https://your-qdrant-instance.qdrant.io
MONGODB_URI=mongodb://localhost:27017

# Optional
VECTOR_DB_API_KEY=your_qdrant_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
MONGODB_DATABASE=newsletter_agent

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
``` 