# AI Recipe Agent API Contract

## Overview

The AI Recipe Agent API is a FastAPI-based service that provides an intelligent agent for recipe recommendations, cooking advice, and newsletter generation. The API supports conversational interactions with an AI agent that can search for recipes, find similar recipes, and build content for newsletters.

**Base URL**: `http://localhost:8000` (development)  
**API Version**: 1.0.0  
**Content Type**: `application/json`

## Authentication

Currently, the API does not require authentication. For production use, implement appropriate authentication mechanisms.

## Endpoints

### 1. Health Check

#### GET `/`

Check the health status of the API service.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Response Model:**
- `status` (string): Service status ("healthy" or "unhealthy")
- `version` (string): API version
- `timestamp` (string): Current UTC timestamp in ISO format

---

### 2. Chat with AI Agent

#### POST `/chat`

Process a chat message through the AI agent. This endpoint accepts natural language queries and returns the AI agent's response. The agent can search for recipes, find similar recipes, and provide cooking advice. The entire conversation is designed to build content for a newsletter.

**Request Body:**
```json
{
  "message": "Find me a quick pasta recipe",
  "chat_id": "optional-chat-id",
  "prompt": "optional-newsletter-prompt"
}
```

**Request Model:**
- `message` (string, required): The user's message (minimum 1 character)
- `chat_id` (string, optional): Chat ID to continue conversation. If null or empty, creates a new chat
- `prompt` (string, optional): Newsletter generation prompt for this chat session

**Response:**
```json
{
  "response": "I found a great quick pasta recipe for you! Here's a simple 20-minute garlic butter pasta...",
  "chat_id": "chat_12345",
  "recipes": [
    {
      "id": "recipe_001",
      "title": "Quick Garlic Butter Pasta",
      "summary": "A simple 20-minute pasta dish with garlic, butter, and herbs",
      "url": "https://example.com/recipe/quick-garlic-pasta",
      "score": 0.95
    }
  ],
  "tool_calls": [
    {
      "tool": "recipe_search",
      "args": {"query": "quick pasta recipe"},
      "result": "Found 5 recipes"
    }
  ]
}
```

**Response Model:**
- `response` (string): The AI agent's response
- `chat_id` (string): The chat ID (new or existing)
- `recipes` (array, optional): Any recipes found during the conversation
  - `id` (string): Recipe unique identifier
  - `title` (string): Recipe title
  - `summary` (string): Recipe summary
  - `url` (string): Recipe URL
  - `score` (float, optional): Relevance or similarity score
- `tool_calls` (array, optional): Information about tools that were called

**Status Codes:**
- `200`: Success
- `404`: Chat not found (when providing invalid chat_id)
- `500`: Internal server error

---

### 3. List All Chats

#### GET `/chats`

Get all chat sessions with their metadata.

**Response:**
```json
{
  "chats": [
    {
      "id": "chat_12345",
      "title": "Quick Weeknight Dinners",
      "prompt": "Create a newsletter about quick weeknight dinner recipes",
      "newsletter": "This week's newsletter features...",
      "created_at": "2024-01-15T10:30:00.000Z",
      "updated_at": "2024-01-15T11:45:00.000Z",
      "message_count": 8
    }
  ]
}
```

**Response Model:**
- `chats` (array): List of all chats
  - `id` (string): Chat unique identifier
  - `title` (string): Chat title
  - `prompt` (string, optional): Newsletter generation prompt for this chat session
  - `newsletter` (string, optional): Newsletter content for this chat session
  - `created_at` (datetime): Chat creation timestamp
  - `updated_at` (datetime): Chat last update timestamp
  - `message_count` (integer): Number of messages in the chat

**Status Codes:**
- `200`: Success
- `500`: Internal server error

---

### 4. Get Specific Chat

#### GET `/chats/{chat_id}`

Get a specific chat with all its messages.

**Path Parameters:**
- `chat_id` (string): The chat ID

**Response:**
```json
{
  "id": "chat_12345",
  "title": "Quick Weeknight Dinners",
  "prompt": "Create a newsletter about quick weeknight dinner recipes",
  "newsletter": "This week's newsletter features...",
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T11:45:00.000Z",
  "message_count": 8,
  "messages": [
    {
      "role": "user",
      "content": "Find me a quick pasta recipe",
      "timestamp": "2024-01-15T10:30:00.000Z"
    },
    {
      "role": "assistant",
      "content": "I found a great quick pasta recipe for you!",
      "timestamp": "2024-01-15T10:30:05.000Z"
    }
  ]
}
```

**Response Model:**
- `id` (string): Chat unique identifier
- `title` (string): Chat title
- `prompt` (string, optional): Newsletter generation prompt
- `newsletter` (string, optional): Newsletter content
- `created_at` (datetime): Chat creation timestamp
- `updated_at` (datetime): Chat last update timestamp
- `message_count` (integer): Number of messages in the chat
- `messages` (array): All messages in the chat
  - `role` (string): Message role ("user" or "assistant")
  - `content` (string): Message content
  - `timestamp` (datetime): Message timestamp

**Status Codes:**
- `200`: Success
- `404`: Chat not found
- `500`: Internal server error

---

### 5. Delete Chat

#### DELETE `/chats/{chat_id}`

Delete a chat and all its messages.

**Path Parameters:**
- `chat_id` (string): The chat ID

**Response:**
```json
{
  "message": "Chat deleted successfully"
}
```

**Status Codes:**
- `200`: Success
- `404`: Chat not found
- `500`: Internal server error

---

### 6. Update Chat Prompt

#### PUT `/chats/{chat_id}/prompt`

Update the newsletter generation prompt for a chat.

**Path Parameters:**
- `chat_id` (string): The chat ID

**Request Body:**
```json
{
  "prompt": "Create a newsletter about healthy breakfast recipes"
}
```

**Request Model:**
- `prompt` (string, required): The newsletter generation prompt

**Response:**
```json
{
  "message": "Chat prompt updated successfully"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing prompt)
- `404`: Chat not found
- `500`: Internal server error

---

### 7. Update Chat Newsletter

#### PUT `/chats/{chat_id}/newsletter`

Update the newsletter content for a chat.

**Path Parameters:**
- `chat_id` (string): The chat ID

**Request Body:**
```json
{
  "newsletter": "This week's newsletter features healthy breakfast recipes..."
}
```

**Request Model:**
- `newsletter` (string, required): The newsletter content

**Response:**
```json
{
  "message": "Chat newsletter updated successfully"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing newsletter content)
- `404`: Chat not found
- `500`: Internal server error

---

### 8. List Available Tools

#### GET `/tools`

List available tools for the AI agent.

**Response:**
```json
{
  "tools": [
    {
      "name": "recipe_search",
      "description": "Search for recipes based on ingredients, cuisine, or dietary restrictions",
      "args_schema": "RecipeSearchArgs(query: str, cuisine: Optional[str] = None, dietary: Optional[str] = None)"
    },
    {
      "name": "find_similar_recipes",
      "description": "Find recipes similar to a given recipe",
      "args_schema": "SimilarRecipeArgs(recipe_id: str, limit: int = 5)"
    }
  ]
}
```

**Response Model:**
- `tools` (array): List of available tools
  - `name` (string): Tool name
  - `description` (string): Tool description
  - `args_schema` (string, optional): Tool arguments schema

**Status Codes:**
- `200`: Success

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error or missing required field"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error description]"
}
```

---

## Usage Examples

### Starting a New Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to make dinner tonight. What should I cook?",
    "prompt": "Create a newsletter about weeknight dinner inspiration"
  }'
```

### Continuing an Existing Chat
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you find me a vegetarian version of that recipe?",
    "chat_id": "chat_12345"
  }'
```

### Getting All Chats
```bash
curl -X GET "http://localhost:8000/chats"
```

### Getting a Specific Chat
```bash
curl -X GET "http://localhost:8000/chats/chat_12345"
```

### Updating a Chat Prompt
```bash
curl -X PUT "http://localhost:8000/chats/chat_12345/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a newsletter about healthy meal prep ideas"
  }'
```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, implement appropriate rate limiting mechanisms.

## CORS

The API includes CORS middleware configured to allow all origins (`*`). For production, configure appropriate CORS settings based on your frontend domain.

## Logging

The API uses Python's logging module with DEBUG level enabled. All requests and responses are logged for debugging purposes.

---

## Version History

- **1.0.0**: Initial release with chat functionality, recipe search, and newsletter generation features 