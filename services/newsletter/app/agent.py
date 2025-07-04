"""AI Agent implementation using OpenAI and LangChain."""

from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.serpapi import SerpAPIWrapper
import logging

from app.tools import get_available_tools
from app.config import get_openai_api_key, get_tavily_api_key, get_serpapi_key

logger = logging.getLogger(__name__)

def create_web_search_tool() -> Tool:
    """Create a web search tool using available APIs."""
    try:
        # Try Tavily first (most reliable)
        if get_tavily_api_key():
            logger.info("Using Tavily for web search")
            return TavilySearchResults(
                api_key=get_tavily_api_key(),
                max_results=5
            )
        # Fallback to SerpAPI
        elif get_serpapi_key():
            logger.info("Using SerpAPI for web search")
            serpapi = SerpAPIWrapper(serpapi_api_key=get_serpapi_key())
            return Tool(
                name="web_search",
                description="Search the web for current information",
                func=serpapi.run
            )
        # Final fallback to DuckDuckGo (no API key required)
        else:
            logger.info("Using DuckDuckGo for web search (no API key required)")
            return DuckDuckGoSearchRun()
    except ImportError as e:
        logger.warning(f"Import error creating web search tool: {e}")
        # If DuckDuckGo is not available, create a simple fallback
        return Tool(
            name="web_search",
            description="Search the web for current information (limited functionality)",
            func=lambda query: f"Web search not available. Please configure TAVILY_API_KEY or SERPAPI_API_KEY for full functionality. Query was: {query}"
        )
    except Exception as e:
        logger.warning(f"Error creating web search tool: {e}")
        return Tool(
            name="web_search", 
            description="Search the web for current information (limited functionality)",
            func=lambda query: f"Web search error: {str(e)}. Query was: {query}"
        )

def create_agent() -> AgentExecutor:
    """Create and configure the AI agent."""
    try:
        # Initialize the language model
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            openai_api_key=get_openai_api_key()
        )
        
        # Get custom tools
        custom_tools = get_available_tools()
        
        # Add web search tool
        web_search_tool = create_web_search_tool()
        all_tools = custom_tools + [web_search_tool]
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant that specializes in recipe recommendations and cooking advice, with the ultimate goal of generating a comprehensive newsletter from the conversation.

Your primary mission is to help users explore recipes, cooking tips, and culinary topics while building content for a newsletter. Every interaction should contribute to creating rich, engaging newsletter content.

You have access to the following tools:
- search_recipes: Search for recipes using natural language queries in our database
- get_similar_recipes: Find recipes similar to a specific recipe by ID in our database
- find_similar_recipes_from_url: Find recipes similar to a recipe from a web URL by extracting its content and searching our database
- search_recipes_with_web_context: Search for recipes and enhance results with current web search context
- web_search: Search the web for current information, trends, and tips

When users ask about recipes:
- Use search_recipes for basic recipe searches in our database
- Use search_recipes_with_web_context when you want to provide current trends and tips along with recipes
- Use find_similar_recipes_from_url when users share a recipe URL and want similar recipes
- Use get_similar_recipes when users reference a recipe by ID from our database

For general questions, current information, cooking trends, or when users ask about specific ingredients or techniques, use web_search to provide up-to-date information.

Always provide helpful, informative responses and explain your reasoning. When possible, combine database results with web search to give the most comprehensive and current information.

Remember: Every conversation is building toward creating a newsletter, so gather diverse content, explore different topics, and ensure the conversation covers multiple recipes, tips, and insights that would make for an engaging newsletter."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(llm, all_tools, prompt)
        
        # Create the agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=all_tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        logger.info("AI agent created successfully")
        return agent_executor
        
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise

# Global agent instance
_agent_executor: AgentExecutor = None

def get_agent() -> AgentExecutor:
    """Get or create the global agent instance."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_agent()
    return _agent_executor

def process_query(query: str, chat_history: List[Dict[str, Any]] = None) -> str:
    """
    Process a user query through the AI agent.
    
    Args:
        query: The user's natural language query
        chat_history: Optional chat history for context
        
    Returns:
        The agent's response as a string
    """
    try:
        logger.info(f"Processing query: {query}")
        
        agent = get_agent()
        
        # Prepare input for the agent
        inputs = {
            "input": query,
            "chat_history": chat_history or []
        }
        
        # Run the agent
        result = agent.invoke(inputs)
        
        logger.info("Query processed successfully")
        return result["output"]
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return f"I encountered an error while processing your request: {str(e)}" 