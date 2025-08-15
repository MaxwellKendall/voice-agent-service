export interface RecipeExtractionRequest {
  url: string
}

export interface RecipeExtractionResponse {
  success: boolean
  data?: {
    title: string
    description?: string
    ingredients: string[]
    instructions: string[]
    prepTime?: string
    cookTime?: string
    totalTime?: string
    servings?: string
    difficulty?: string
    cuisine?: string
    tags?: string[]
    image?: string
  }
  error?: string
}

const RECIPE_API_URL = 'https://mcp-production-9ebf.up.railway.app/extract-recipe'

export const extractRecipe = async (url: string): Promise<RecipeExtractionResponse> => {
  try {
    const response = await fetch(`${RECIPE_API_URL}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error extracting recipe:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to extract recipe'
    }
  }
}
