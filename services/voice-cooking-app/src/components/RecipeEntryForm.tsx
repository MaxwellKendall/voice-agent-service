import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

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

      const response = await fetch('http://localhost:8000/extract-and-store-recipe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ recipe_url: url.trim() }),
      })

      if (!response.ok) {
        throw new Error(`Failed to extract recipe: ${response.status}`)
      }

      const data = await response.json()

      if (data.success && data.recipe) {
        // Navigate to the recipe detail page
        navigate(`/realtime/${data.recipe.id}`)
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
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        <div>
          <label htmlFor="recipe-url" className="block text-sm font-medium text-gray-700 mb-2">
            Recipe URL
          </label>
          <div className="relative">
            <input
              type="url"
              id="recipe-url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/recipe"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 focus:border-gray-900 transition-colors"
              disabled={isLoading}
            />
            {isLoading && (
              <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>
              </div>
            )}
          </div>
          <p className="mt-2 text-sm text-gray-500">
            Paste a URL from any cooking website to extract the recipe
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <svg className="w-5 h-5 text-red-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="w-full bg-gray-900 text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Extracting Recipe...' : 'Extract Recipe'}
        </button>
      </form>

      {/* Supported Sites Info */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Supported Websites</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            'AllRecipes',
            'Food Network',
            'Epicurious',
            'Bon Appétit',
            'Serious Eats',
            'King Arthur',
            'Taste of Home',
            'And many more...'
          ].map((site) => (
            <div key={site} className="text-xs text-gray-600 bg-gray-50 px-3 py-2 rounded">
              {site}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RecipeEntryForm
