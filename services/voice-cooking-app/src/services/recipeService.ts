export interface RecipeExtractionRequest {
  url: string
}

export interface RecipeExtractionResponse {
  success: boolean
  recipe_id?: string
  title?: string
  link?: string
  summary?: string
  ingredients?: string[]
  instruction_details?: string[]
  cuisine?: string
  category?: string
  difficulty_level?: number
  servings?: number
  prep_time?: number
  cook_time?: number
  error?: string
}

export interface RecipeByIdResponse {
  success: boolean
  recipe?: {
    _id: string
    title: string
    description?: string
    ingredients: string[]
    instruction_details: string[]
    prepTime?: string
    cookTime?: string
    totalTime?: string
    servings?: string
    difficulty?: string
    cuisine?: string
    tags?: string[]
    image?: string
    link?: string
    summary?: string
    category?: string
    difficulty_level?: number
    prep_time?: number
    cook_time?: number
  }
  error?: string
}

export interface RecipeSearchResponse {
  success: boolean
  recipes?: Array<{
    mongo_id: string
    title: string
    description?: string
    ingredients: string[]
    instruction_details: string[]
    prepTime?: string
    cookTime?: string
    totalTime?: string
    servings?: string[]
    difficulty?: string
    cuisine?: string
    tags?: string[]
    image_url?: string
    link?: string
    summary?: string
    category?: string
    difficulty_level?: number
    prep_time?: number
    cook_time?: number
    rating?: number
    rating_count?: number
  }>
  error?: string
}

const RECIPE_API_URL = import.meta.env.VITE_RECIPE_API_URL || 'http://localhost:8000';

export const extractRecipe = async (url: string): Promise<RecipeExtractionResponse> => {
  try {
    const response = await fetch(`${RECIPE_API_URL}/extract-and-store-recipe`, {
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

export const getRecipeById = async (recipeId: string): Promise<RecipeByIdResponse> => {
  try {
    const response = await fetch(`${RECIPE_API_URL}/recipe/${recipeId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      if (response.status === 404) {
        return {
          success: false,
          error: 'Recipe not found'
        }
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching recipe:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to fetch recipe'
    }
  }
}

export const searchRecipes = async (query: string): Promise<RecipeSearchResponse> => {
  try {
    const response = await fetch(`${RECIPE_API_URL}/search-recipes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data;
  } catch (error) {
    console.error('Error searching recipes:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to search recipes'
    }
  }
}
