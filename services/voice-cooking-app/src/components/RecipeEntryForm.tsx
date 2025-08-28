import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface RecipeEntryFormProps {
  onSuccess: () => void
}

const RecipeEntryForm: React.FC<RecipeEntryFormProps> = ({ onSuccess }) => {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!url.trim()) {
      setError('Please enter a recipe URL')
      return
    }

    try {
      setIsLoading(true)
      setError(null)

      const response = await fetch(`${BASE_URL}/extract-and-store-recipe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      })

      if (!response.ok) {
        throw new Error(`Failed to extract recipe: ${response.status}`)
      }

      const data = await response.json()

      if (data.success && data.recipe_id) {
        // Clear the form
        setUrl('')
        // Navigate to the dashboard with the recipe ID
        navigate(`/dashboard/${data.recipe_id}`)
        onSuccess()
      } else {
        throw new Error(data.error || 'Failed to extract recipe')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to extract recipe: ${errorMessage}`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <form onSubmit={handleSubmit} className="relative">
        {/* URL Input with integrated submit button */}
        <div className="relative">
          <input
            type="url"
            id="recipe-url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste a recipe URL from any cooking website..."
            className="w-full px-4 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-gray-900 transition-colors text-sm"
            disabled={isLoading}
          />
          
          {/* Submit button with arrow icon */}
          <button
            type="submit"
            disabled={isLoading || !url.trim()}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-400 hover:text-gray-600 disabled:text-gray-300 disabled:cursor-not-allowed transition-colors rounded-lg hover:bg-gray-100"
            aria-label="Extract recipe"
          >
            {isLoading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
            ) : (
              <svg 
                className="w-4 h-4" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" 
                />
              </svg>
            )}
          </button>
        </div>
        
        <p className="text-xs text-gray-500">
          Supports AllRecipes, Food Network, Epicurious, and many more cooking sites
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
