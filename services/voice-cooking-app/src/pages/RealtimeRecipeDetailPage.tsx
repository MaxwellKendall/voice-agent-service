import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { RecipeExtractionResponse } from '../services/recipeService'
import RealtimeCookMode from '../components/RealtimeCookMode'
import RealtimeRecipeDisplay from '../components/RealtimeRecipeDisplay'

const RealtimeRecipeDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [recipe, setRecipe] = useState<RecipeExtractionResponse['data'] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCookMode, setIsCookMode] = useState(false)

  useEffect(() => {
    const fetchRecipe = async () => {
      if (!id) return

      try {
        setLoading(true)
        setError(null)
        
        const response = await fetch(`http://localhost:8000/recipe/${id}`)
        
        if (!response.ok) {
          throw new Error(`Failed to fetch recipe: ${response.status}`)
        }
        
        const data = await response.json()
        
        if (data.success) {
          setRecipe(data.recipe)
        } else {
          throw new Error(data.error || 'Failed to fetch recipe')
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Unknown error'
        setError(`Error loading recipe: ${errorMessage}`)
      } finally {
        setLoading(false)
      }
    }

    fetchRecipe()
  }, [id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading recipe...</p>
        </div>
      </div>
    )
  }

  if (error || !recipe) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-6">
        <div className="max-w-md w-full text-center">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <h2 className="text-lg font-medium text-gray-900 mb-2">Recipe Not Found</h2>
            <p className="text-gray-600 mb-6">{error || 'The recipe you are looking for could not be found.'}</p>
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-gray-900 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-800 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (isCookMode) {
    return <RealtimeCookMode recipe={recipe} onExit={() => setIsCookMode(false)} />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-medium text-gray-900">Recipe Details</h1>
              <p className="text-sm text-gray-500">View and cook with voice assistance</p>
            </div>
          </div>
          <button
            onClick={() => setIsCookMode(true)}
            className="bg-gray-900 text-white px-6 py-2 rounded-lg font-medium hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
          >
            Start Voice Cooking
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <RealtimeRecipeDisplay recipe={recipe} />
      </div>
    </div>
  )
}

export default RealtimeRecipeDetailPage
