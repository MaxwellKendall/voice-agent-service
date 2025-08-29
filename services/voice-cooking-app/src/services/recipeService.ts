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

const RECIPE_API_URL = import.meta.env.VITE_RECIPE_API_URL ?? 'http://localhost:8000';

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
    return data || { success: false, error: 'No data received' };
  } catch (error) {
    console.error('Error searching recipes:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to search recipes'
    }
  }
}

// User Recipe Management Interfaces
export interface SaveRecipeResponse {
  success: boolean
  message?: string
  error?: string
}

export interface UserSavedRecipesResponse {
  success: boolean
  data?: Array<{
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
    saved_at?: string
  }>
  pagination?: {
    page: number
    limit: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  error?: string
}

export interface IsRecipeSavedResponse {
  success: boolean
  is_saved?: boolean
  error?: string
}

// User Recipe Management Functions
export const saveRecipeForUser = async (userId: string, recipeId: string): Promise<SaveRecipeResponse> => {
  try {
    const response = await fetch(`${RECIPE_API_URL}/user/${userId}/recipe/${recipeId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error saving recipe for user:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to save recipe'
    }
  }
}

export const getUserSavedRecipes = async (userId: string, page: number = 1, limit: number = 20): Promise<UserSavedRecipesResponse> => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    })
    
    const response = await fetch(`${RECIPE_API_URL}/user/${userId}/recipes?${params}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error getting user saved recipes:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get saved recipes'
    }
  }
}

export const removeSavedRecipe = async (userId: string, recipeId: string): Promise<SaveRecipeResponse> => {
  try {
    const response = await fetch(`${RECIPE_API_URL}/user/${userId}/recipe/${recipeId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error removing saved recipe:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to remove saved recipe'
    }
  }
}

export const getUserRecipe = async (userId: string, recipeId: string): Promise<RecipeByIdResponse> => {
  try {
    const response = await fetch(`${RECIPE_API_URL}/user/${userId}/recipe/${recipeId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      if (response.status === 404) {
        return {
          success: false,
          error: 'Recipe not found in user\'s saved recipes'
        }
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error getting user recipe:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to get user recipe'
    }
  }
}

export const isRecipeSavedForUser = async (userId: string, recipeId: string): Promise<IsRecipeSavedResponse> => {
  try {
    const response = await fetch(`${RECIPE_API_URL}/user/${userId}/recipe/${recipeId}/saved`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error checking if recipe is saved:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to check if recipe is saved'
    }
  }
}
