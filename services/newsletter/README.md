# AI Recipe Agent

A minimal AI agent built with OpenAI, LangChain, and FastAPI that provides recipe recommendations and cooking advice. The agent uses a vector database (Qdrant) for semantic recipe search and supports web search capabilities.

## Features

- **Recipe Search**: Find recipes using natural language queries
- **Similar Recipe Discovery**: Find recipes similar to a specific recipe
- **Web Search Integration**: Access current information via Tavily/SerpAPI/DuckDuckGo
- **FastAPI Backend**: RESTful API with CORS support
- **Vector Database**: Semantic search using Qdrant
- **Comprehensive Testing**: Unit and integration tests

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Qdrant vector database (cloud or local)
- Optional: Tavily or SerpAPI keys for enhanced web search

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd newsletter
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

The server will start on `http://localhost:8000` with auto-reload enabled.

## Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
VECTOR_DB_API_KEY=your_qdrant_api_key_here
VECTOR_DB_URL=https://your-qdrant-instance.qdrant.io
TAVILY_API_KEY=your_tavily_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

## API Usage

### Health Check
```bash
curl http://localhost:8000/
```

### Chat with AI Agent
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are some easy Mexican recipes?",
    "chat_history": []
  }'
```

### List Available Tools
```bash
curl http://localhost:8000/tools
```

## Example Queries

The AI agent can handle various natural language queries:

- "What are some easy Mexican recipes?"
- "What's similar to this turkey chili?"
- "Find vegetarian pasta dishes"
- "Show me quick breakfast recipes"
- "What are the health benefits of quinoa?"

## Project Structure

```
newsletter/
├── app/
│   ├── __init__.py
│   ├── api.py          # FastAPI application
│   ├── agent.py        # AI agent implementation
│   ├── config.py       # Configuration management
│   ├── models.py       # Pydantic models
│   ├── tools.py        # Custom tools
│   └── vector_store.py # Qdrant operations
├── tests/
│   ├── __init__.py
│   ├── test_api.py     # Integration tests
│   └── test_tools.py   # Unit tests
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── env.example         # Environment variables template
└── README.md          # This file
```

## Custom Tools

### `searchRecipes(query: str)`
Searches for recipes using semantic similarity in the vector database.

**Parameters:**
- `query`: Natural language description of desired recipes

**Returns:** List of recipes with title, summary, URL, and relevance score

### `getSimilarRecipes(id: str)`
Finds recipes similar to a specific recipe by ID.

**Parameters:**
- `id`: Recipe unique identifier

**Returns:** List of similar recipes with similarity scores

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_tools.py

# Run with verbose output
pytest -v
```

## Development

### Running in Development Mode

The application runs with auto-reload by default:

```bash
python main.py
```

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Logging

The application uses structured logging with DEBUG level in development. Check the console output for detailed logs.

## Architecture

### Functional Design

The application follows a functional programming approach with:

- **Pure functions**: Each function has a single responsibility
- **Immutable data**: Pydantic models ensure data integrity
- **Composition**: Functions are composed to build complex operations
- **Type safety**: Full type annotations throughout

### Key Components

1. **Vector Store**: Handles Qdrant operations for recipe search
2. **Tools**: Custom LangChain tools for recipe operations
3. **Agent**: OpenAI-powered agent with tool calling capabilities
4. **API**: FastAPI server with CORS and validation
5. **Configuration**: Environment-based configuration management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License. 