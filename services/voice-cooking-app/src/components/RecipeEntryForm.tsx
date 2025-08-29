import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCircleArrowUp, faCircleXmark } from '@fortawesome/free-solid-svg-icons'
import { extractRecipe } from '../services/recipeService'
import { searchRecipes } from '../services/recipeService'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface RecipeEntryFormProps {
  onSuccess: () => void
  onSearchResults?: (recipes: any[]) => void
}

const RecipeEntryForm: React.FC<RecipeEntryFormProps> = ({ onSuccess, onSearchResults }) => {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  // Helper function to detect if input is a URL
  const isUrl = (text: string): boolean => {
    try {
      new URL(text)
      return true
    } catch {
      return false
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim()) {
      setError('Please enter a recipe URL or search query')
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      if (isUrl(input.trim())) {
        // Handle URL extraction
        const response = await extractRecipe(input.trim())
        
        if (response.success && response.recipe_id) {
          // Navigate to the dashboard with the recipe ID
          navigate(`/dashboard/${response.recipe_id}`)
          onSuccess()
        } else {
          throw new Error(response.error || 'Failed to extract recipe')
        }
      } else {
        // Handle natural language search
        const searchResponse = await searchRecipes(input.trim())
        
        if (searchResponse.success && searchResponse.recipes) {
          // Transform recipes to match our interface
          const transformedRecipes = searchResponse.recipes.map(recipe => ({
            id: recipe.mongo_id,
            title: recipe.title,
            image: recipe.image_url,
            summary: recipe.summary,
            description: recipe.description,
            tags: recipe.tags,
            cuisine: recipe.cuisine,
            category: recipe.category,
            prepTime: recipe.prepTime || (recipe.prep_time ? `${recipe.prep_time} minutes` : undefined),
            cookTime: recipe.cookTime || (recipe.cook_time ? `${recipe.cook_time} minutes` : undefined),
            servings: recipe.servings,
            rating: recipe.rating,
            ratingCount: recipe.rating_count
          }))
          
          // Call the search results callback
          onSearchResults?.(transformedRecipes)
        } else {
          throw new Error(searchResponse.error || 'Failed to search recipes')
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to process request: ${errorMessage}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setInput('')
    setError(null)
  }

  const canSubmit = input.trim().length > 0 && !isLoading
  const showClearButton = error && input.trim().length > 0

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="relative">
        {/* URL Input with integrated submit button */}
        <div className="relative">
          <input
            type="text"
            id="recipe-input"
            value={input}
            onChange={(e) => {
              setInput(e.target.value)
              // Clear error when user starts typing
              if (error) setError(null)
            }}
            placeholder="Paste a recipe URL or search for recipes (e.g., 'quick pasta dishes')..."
            className="w-full px-4 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-gray-900 transition-colors text-sm"
            disabled={isLoading}
          />
          
          {/* Submit button or Clear button */}
          <button
            type={showClearButton ? "button" : "submit"}
            onClick={showClearButton ? handleClear : undefined}
            disabled={!canSubmit && !showClearButton}
            className={`absolute flex right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-full transition-all duration-200 ${
              showClearButton 
                ? 'text-red-600 hover:text-red-700' 
                : canSubmit 
                  ? 'text-blue-600 hover:text-blue-700' 
                  : 'text-gray-300 cursor-not-allowed'
            }`}
            aria-label={showClearButton ? "Clear input" : "Extract recipe"}
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
            ) : showClearButton ? (
              <FontAwesomeIcon 
                icon={faCircleXmark} 
                className="w-5 h-5" 
              />
            ) : (
              <FontAwesomeIcon 
                icon={faCircleArrowUp} 
                className="w-5 h-5" 
              />
            )}
          </button>
        </div>
        
        <p className="text-xs mt-2 text-gray-500">
          Import recipes from your favorite websites or search for recipes with natural language.
        </p>
      </form>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex">
            <svg className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-2">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default RecipeEntryForm
