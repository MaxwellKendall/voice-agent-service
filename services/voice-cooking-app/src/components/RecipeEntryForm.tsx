import React, { JSX,useState } from 'react'
import { extractRecipe, RecipeExtractionResponse } from '../services/recipeService'

interface RecipeEntryFormProps {
  onRecipeExtracted: (recipe: RecipeExtractionResponse) => void
}

const RecipeEntryForm = ({ onRecipeExtracted }: RecipeEntryFormProps): JSX.Element => {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [urlError, setUrlError] = useState<string | null>(null)

  const validateUrl = (url: string): boolean => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    console.log('URL input changed:', value) // Debug log
    setUrl(value)
    setError(null)
    
    if (value && !validateUrl(value)) {
      setUrlError('Please enter a valid URL')
    } else {
      setUrlError(null)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!url.trim()) {
      setError('Please enter a recipe URL')
      return
    }

    if (!validateUrl(url)) {
      setError('Please enter a valid URL')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await extractRecipe(url)
      
      if (result.success) {
        onRecipeExtracted(result)
        setUrl('')
      } else {
        setError(result.error || 'Failed to extract recipe')
      }
    } catch (err) {
      setError('An unexpected error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Add a Recipe
      </h3>
      <p className="text-gray-600 mb-6">
        Paste any recipe URL and we'll extract the ingredients and instructions for you.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="recipe-url" className="block text-sm font-medium text-gray-700 mb-2">
            Recipe URL
          </label>
          <input
            type="url"
            id="recipe-url"
            value={url}
            onChange={handleUrlChange}
            placeholder="https://example.com/recipe"
            className={`w-full px-3 py-2 border rounded-md shadow-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              urlError ? 'border-red-300' : 'border-gray-300'
            }`}
            disabled={isLoading}
          />
          {urlError && (
            <p className="mt-1 text-sm text-red-600">{urlError}</p>
          )}
          {/* Debug: Show current URL value */}
          {url && (
            <p className="mt-1 text-xs text-gray-500">Current URL: {url}</p>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading || !url.trim() || !!urlError}
          className={`w-full flex justify-center items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 ${
            isLoading || !url.trim() || !!urlError
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Extracting Recipe...
            </>
          ) : (
            'Extract Recipe'
          )}
        </button>
      </form>

      <div className="mt-4 text-xs text-gray-500">
        <p>Supported sites: Most recipe websites including AllRecipes, Food Network, Epicurious, and more.</p>
      </div>
    </div>
  )
}

export default RecipeEntryForm
