You are an expert Python developer building a minimal AI agent using OpenAI + LangChain + FastAPI. Your goal is to create a simple backend server that supports tool-calling via OpenAI's function calling and exposes two custom recipe-related tools using a vector database (Qdrant).

## Requirements

1. **Set up an agent using OpenAI (gpt-4 or gpt-4o)** and LangChain that can:
   - Handle web search via Tavily or SerpAPI
   - Call custom tools via structured tool definitions
   - Route natural language queries like:
     - “What are some easy Mexican recipes?”
     - “What’s similar to this turkey chili?”

2. **Implement these tools**:

   ### `searchRecipes(query: str) -> List[dict]`
   - Accepts a user query string
   - Uses a pre-initialized Qdrant vector store to do a semantic search
   - Returns up to 5 recipes as a list of dicts with title, summary, url

   ### `getSimilarRecipes(id: str) -> List[dict]`
   - Uses the vector of a known recipe (by ID) to return similar recipes

3. **Use FastAPI as the server interface**
   - Expose a POST endpoint `/chat` that accepts a natural language prompt
   - Returns the AI’s full response including any tool calls
   - Support CORS for local frontend testing

4. **Add testing**
   - Write unit tests for the two tools using `pytest`
   - Use a mock Qdrant client for tests

5. **Enable debugging and dev setup**
   - Include a `.env` file for API keys
   - Use `uvicorn` to launch the app with `--reload`
   - Output logs at DEBUG level

6. **Organize files clearly**

7. **Coding Style**
  - Implemnet a functional approach rather than an object oriented one, focusing on encapsulated, composable functions that are expressive
  - Each function should be annotated with types
  - Provide helpful comments, but be concise

8. **Environment Variables**
  - Use dotenv for laoding the environment
  - Assume you have access to the following variables
  ```
    OPENAI_API_KEY
    VECTOR_DB_API_KEY
    VECTOR_DB_URL
  ```