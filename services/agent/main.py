import os
from agents import Agent, Runner, function_tool, WebSearchTool, FileSearchTool, set_default_openai_key, trace
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from dotenv import load_dotenv

load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))
PROPRIETARY_RECIPE_VECTOR_STORE_ID = os.getenv("PROPRIETARY_RECIPE_VECTOR_STORE_ID")

'''
AGENTS DEFINTION:
> the beauty of the Agents SDK is that it is incredibly easy to extend and add aditional agents to the workflow when you want to add new functionality
''' 
recipe_finder_agent = Agent(
    name="RecipeFinderAgent",
    model="gpt-4o-mini",
    tools=[WebSearchTool(), FileSearchTool(max_num_results=3, vector_store_id=PROPRIETARY_RECIPE_VECTOR_STORE_ID)],
)
recipe_detail_agent = Agent(
    name="RecipeDetailAgent",
    model="gpt-4o-mini",
    tools=[WebSearchTool(), FileSearchTool(max_num_results=3, vector_store_id=PROPRIETARY_RECIPE_VECTOR_STORE_ID)],
)
meal_plan_agent = Agent(
    name="MealPlanAgent",
    model="gpt-4o-mini",
    tools=[WebSearchTool(), FileSearchTool(max_num_results=3, vector_store_id=PROPRIETARY_RECIPE_VECTOR_STORE_ID)],
)
router_agent = Agent(
    name="RouterAgent",
    model="gpt-4o-mini",
    instructions=prompt_with_handoff_instructions(
"""
You are the virtual assistant for the Cooking Assistant App. Welcome the user and ask how you can help.
Based on the user's intent, route to:
- RecipeFinderAgent: for users browsing or looking for a new recipe
- RecipeDetailAgent: for users who know the recipe they want to cook
- MealPlanAgent: for users who are looking to plan out more than one meal
"""),
    handoffs=[recipe_finder_agent, recipe_detail_agent, meal_plan_agent]
)

# %%
async def test_queries():
    examples = [
        "I'm looking for a recipe, can you help me find one?", # RecipeFinderAgent test
        "I have a recipe for chicken parmesean, what is the first step?", # RecipeDetailAgent test
        "I need to plan meals for the next few days, can you help me?", # MealPlanAgent test
    ]
    with trace("Cooking Assistant App"):
        for query in examples:
            result = await Runner.run(router_agent, query)
            print(f"User: {query}")
            print(result.final_output)
            print("---")
# Run the tests
if __name__ == "__main__":
    import asyncio
    
    async def main():
        await test_queries()
    
    # This allows you to use await directly in the script
    asyncio.run(main())




