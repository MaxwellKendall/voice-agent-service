import React, { JSX, useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import RealtimeRecipeDisplay from '../components/RealtimeRecipeDisplay'
import RealtimeCookMode from '../components/RealtimeCookMode'
import { getRecipeById, RecipeByIdResponse } from '../services/recipeService'

const RealtimeRecipeDetailPage = (): JSX.Element => {
  const { recipeId } = useParams<{ recipeId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [recipe, setRecipe] = useState<RecipeByIdResponse['recipe'] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isCookModeActive, setIsCookModeActive] = useState(false)

  useEffect(() => {
    const fetchRecipe = async () => {
      if (!recipeId) {
        setError('No recipe ID provided')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        
        const response = await getRecipeById(recipeId)
        
        if (response.success && response.recipe) {
          setRecipe(response.recipe)
        } else {
          setError(response.error || 'Failed to fetch recipe')
        }
      } catch (err) {
        setError('An unexpected error occurred')
        console.error('Error fetching recipe:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchRecipe()
  }, [recipeId])

  const handleStartCooking = () => {
    setIsCookModeActive(true)
  }

  const handleExitCookMode = () => {
    setIsCookModeActive(false)
  }

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  const handleAddAnotherRecipe = () => {
    navigate('/dashboard')
  }

  // Helper function to format time values
  const formatTime = (timeValue: any): string | undefined => {
    if (!timeValue) return undefined
    
    // If it's already a string, check if it contains "minutes"
    if (typeof timeValue === 'string') {
      if (timeValue.toLowerCase().includes('minutes')) {
        if (timeValue === '0 minutes') {
          return '--'
        }
        return timeValue
      }
      // If it's a number as string, add minutes
      if (!isNaN(Number(timeValue))) {
        const numValue = Number(timeValue)
        return numValue === 0 ? '--' : `${timeValue} minutes`
      }
      return timeValue
    }
    
    // If it's a number, add minutes
    if (typeof timeValue === 'number') {
      return timeValue === 0 ? '--' : `${timeValue} minutes`
    }
    
    return String(timeValue)
  }

  // Transform the recipe data to match the RealtimeRecipeDisplay component's expected format
  const transformedRecipe = {
    success: true,
    data: {
      success: true,
      id: recipe?._id,
      title: recipe?.title,
      description: recipe?.description,
      ingredients: recipe?.ingredients,
      instructions: recipe?.instruction_details,
      prepTime: formatTime(recipe?.prep_time),
      cookTime: formatTime(recipe?.cook_time),
      totalTime: formatTime(recipe?.total_time),
      servings: recipe?.servings,
      cuisine: recipe?.cuisine,
      difficulty: recipe?.difficulty,
      tags: recipe?.tags,
      image: recipe?.image,
      difficulty_level: recipe?.difficulty_level,
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading recipe...</p>
        </div>
      </div>
    )
  }

  if (error || !recipe) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Recipe Not Found</h1>
          <p className="text-gray-600 mb-6">{error || 'The recipe you\'re looking for doesn\'t exist.'}</p>
          <div className="space-y-3">
            <button
              onClick={handleBackToDashboard}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Back to Dashboard
            </button>
            <button
              onClick={handleAddAnotherRecipe}
              className="w-full border-2 border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Add Another Recipe
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <button
                  onClick={handleBackToDashboard}
                  className="mr-4 text-gray-500 hover:text-gray-700 transition-colors p-2 rounded-full hover:bg-gray-100"
                  aria-label="Back to dashboard"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    Recipe Details
                  </h1>
                  {/* Breadcrumb Navigation */}
                  <nav className="flex items-center space-x-2 text-sm text-gray-500 mt-1">
                    <Link 
                      to="/dashboard" 
                      className="hover:text-blue-600 transition-colors"
                    >
                      Dashboard
                    </Link>
                    <span>/</span>
                    <span className="text-gray-700 font-medium truncate max-w-xs">
                      {recipe.title}
                    </span>
                  </nav>
                </div>
              </div>
              
              {/* Recipe Actions */}
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleAddAnotherRecipe}
                  className="text-gray-500 hover:text-gray-700 transition-colors p-2 rounded-full hover:bg-gray-100"
                  aria-label="Add another recipe"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </button>
                <button
                  onClick={() => {
                    // Copy current URL to clipboard
                    navigator.clipboard.writeText(window.location.href)
                      .then(() => {
                        // You could add a toast notification here
                        console.log('Recipe URL copied to clipboard')
                      })
                      .catch(err => {
                        console.error('Failed to copy URL:', err)
                      })
                  }}
                  className="text-gray-500 hover:text-gray-700 transition-colors p-2 rounded-full hover:bg-gray-100"
                  aria-label="Copy recipe link"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="py-8">
          {isCookModeActive ? (
            <RealtimeCookMode
              recipe={transformedRecipe.data}
              onExit={handleExitCookMode}
            />
          ) : (
            <RealtimeRecipeDisplay
              recipe={transformedRecipe.data}
              onStartCooking={handleStartCooking}
              onBack={handleAddAnotherRecipe}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default RealtimeRecipeDetailPage
