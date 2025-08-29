import React, { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import RecipeEntryForm from '../components/RecipeEntryForm'
import RecipeDisplay from '../components/RecipeDisplay'
import RecipeCard from '../components/RecipeCard'
import { getRecipeById, RecipeByIdResponse, getUserSavedRecipes, removeSavedRecipe, saveRecipeForUser } from '../services/recipeService'
export interface Recipe {
  id?: string
  _id?: string
  title: string
  image?: string
  summary?: string
  description?: string
  tags?: string[]
  cuisine?: string
  category?: string
  prepTime?: string
  cookTime?: string
  servings?: string[]
  rating?: number
  ratingCount?: number
} 
const DashboardPage: React.FC = () => {
  const { recipeId } = useParams<{ recipeId: string }>()
  const { user, signOut } = useAuth()
  const navigate = useNavigate()
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  
  // Recipe state
  const [recipe, setRecipe] = useState<RecipeByIdResponse['recipe'] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Search state
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [hasSearchResults, setHasSearchResults] = useState(false)
  
  // Saved recipes state
  const [savedRecipes, setSavedRecipes] = useState<any[]>([])
  const [savedRecipesLoading, setSavedRecipesLoading] = useState(false)

  useEffect(() => {
    if (!user) {
      navigate('/')
    }
  }, [user, navigate])

  // Fetch recipe when recipeId changes
  useEffect(() => {
    const fetchRecipe = async () => {
      if (!recipeId) {
        setRecipe(null)
        setError(null)
        // Clear search results when no recipeId (back to dashboard)
        setHasSearchResults(false)
        setSearchResults([])
        return
      }

      try {
        setLoading(true)
        setError(null)
        
        // Clear search results when viewing a specific recipe
        setHasSearchResults(false)
        setSearchResults([])
        
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

  // Fetch saved recipes when no recipeId and no search results
  useEffect(() => {
    const fetchSavedRecipes = async () => {
      if (!user?.id || recipeId || hasSearchResults) return

      try {
        setSavedRecipesLoading(true)
        const response = await getUserSavedRecipes(user.id)
        
        if (response.success && response.data) {
          setSavedRecipes(response.data.map(r => ({ ...r, image: r.image_url })))
        } else {
          setSavedRecipes([])
        }
      } catch (err) {
        console.error('Error fetching saved recipes:', err)
        setSavedRecipes([])
      } finally {
        setSavedRecipesLoading(false)
      }
    }

    fetchSavedRecipes()
  }, [user?.id, recipeId, hasSearchResults])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleRecipeSuccess = () => {
    // Recipe form submission was successful, recipe will be fetched via useEffect
  }

  const handleSearchResults = (recipes: any[]) => {
    setSearchResults(recipes)
    setHasSearchResults(true)
    setRecipe(null) // Clear any existing recipe view
  }

  const handleBackToDashboard = () => {
    navigate('/dashboard')
  }

  const handleSaveClick = async (e: React.MouseEvent, isSaved = false, recipe: Recipe) => {
    e.stopPropagation()
    if (!user || !recipe.id || loading) return

    setLoading(true)
    try {
      const shouldRemove = isSaved;
      const response = isSaved ? await removeSavedRecipe(user.id, recipe.id) : await saveRecipeForUser(user.id, recipe.id)
      if (response.success) {
        setSavedRecipes(shouldRemove ? savedRecipes.filter(r => r.id !== recipe.id) : [...savedRecipes, recipe])
      }
    } catch (error) {
      console.error('Error toggling save status:', error)
    } finally {
      setLoading(false)
    }
  }

  // Render main content based on current state
  const renderMainContent = () => {
    // If there's a recipeId in the URL, always show recipe details (if loading, error, or success)
    if (recipeId) {
      if (loading) {
        return (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading recipe...</p>
          </div>
        )
      }

      if (error) {
        return (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="text-red-500 text-6xl mb-4">😕</div>
            <h1 className="text-xl font-semibold text-gray-900 mb-2">Recipe Not Found</h1>
            <p className="text-gray-600 mb-6">
              {error || 'The recipe you\'re looking for doesn\'t exist or has been removed.'}
            </p>
            <button
              onClick={handleBackToDashboard}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold transition-colors duration-200"
            >
              Back to Dashboard
            </button>
          </div>
        )
      }

      if (recipe) {
        return (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <RecipeDisplay
              recipe={transformedRecipe.data}
              onBack={handleBackToDashboard}
            />
          </div>
        )
      }
    }

    // If no recipeId, show search results or saved recipes
    if (hasSearchResults && searchResults.length > 0) {
      return (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              Search Results ({searchResults.length})
            </h2>
            <button
              onClick={() => {
                setHasSearchResults(false)
                setSearchResults([])
              }}
              className="text-gray-600 hover:text-gray-900 transition-colors duration-200"
            >
              Clear Results
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {searchResults.map((recipe, index) => (
              <RecipeCard
                key={recipe.id || recipe._id || index}
                recipe={recipe}
                onClick={() => navigate(`/dashboard/${recipe.id || recipe._id}`)}
                userId={user?.id}
                isSaved={savedRecipes.some(r => r.id === recipe.id)}
                handleSaveClick={handleSaveClick}
              />
            ))}
          </div>
        </div>
      )
    }

    // Show saved recipes if no search results and no recipeId
    if (!recipeId && !hasSearchResults) {
      if (savedRecipesLoading) {
        return (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your saved recipes...</p>
          </div>
        )
      }

      if (savedRecipes.length > 0) {
        return (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Your Saved Recipes ({savedRecipes.length})
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {savedRecipes.map((recipe, index) => (
                <RecipeCard
                  key={recipe.id || index}
                  recipe={recipe}
                  onClick={() => navigate(`/dashboard/${recipe.id}`)}
                  userId={user?.id}
                  isSaved={true}
                  handleSaveClick={handleSaveClick}
                />
              ))}
            </div>
          </div>
        )
      }

      // No saved recipes - show welcome content
      return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0 0C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h2 className="text-2xl font-medium text-gray-900 mb-3">Welcome to Your Recipe Collection</h2>
            <p className="text-gray-600 mb-6">
              Add recipes from URLs or search for recipes to build your personal collection. 
              Your saved recipes will appear here for easy access.
            </p>
            <p className="text-sm text-gray-500">
              Use the form above to add your first recipe!
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Voice Cooking Assistant</h3>
              <p className="text-sm text-gray-600">
                Get hands-free guidance through recipes with our AI-powered voice assistant.
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Save Your Favorites</h3>
              <p className="text-sm text-gray-600">
                Save recipes you love to your personal collection for quick access.
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Smart Search</h3>
              <p className="text-sm text-gray-600">
                Search for recipes using natural language or paste recipe URLs.
              </p>
            </div>
          </div>
        </div>
      )
    }

    // This should never be reached, but just in case
    return null
  }

  // Helper function to format time values
  const formatTime = (timeValue: any): string | undefined => {
    if (!timeValue) return undefined
    
    if (typeof timeValue === 'string') {
      if (timeValue.toLowerCase().includes('minutes')) {
        if (timeValue === '0 minutes') {
          return '--'
        }
        return timeValue
      }
      if (!isNaN(Number(timeValue))) {
        const numValue = Number(timeValue)
        return numValue === 0 ? '--' : `${timeValue} minutes`
      }
      return timeValue
    }
    
    if (typeof timeValue === 'number') {
      return timeValue === 0 ? '--' : `${timeValue} minutes`
    }
    
    return String(timeValue)
  }

  // Transform the recipe data to match the RecipeDisplay component's expected format
  const transformedRecipe = {
    success: true,
    data: {
      success: true,
      id: recipe?._id,
      title: recipe?.title,
      description: recipe?.description,
      ingredients: recipe?.ingredients,
      instructions: recipe?.instruction_details,
      prepTime: formatTime(recipe?.prepTime || recipe?.prep_time),
      cookTime: formatTime(recipe?.cookTime || recipe?.cook_time),
      totalTime: formatTime(recipe?.totalTime),
      servings: recipe?.servings,
      difficulty: recipe?.difficulty,
      cuisine: recipe?.cuisine,
      tags: recipe?.tags,
      image: recipe?.image,
      link: recipe?.link,
      summary: recipe?.summary,
      category: recipe?.category,
      difficulty_level: recipe?.difficulty_level
    }
  }

  if (!user) {
    return null
  }



  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-medium text-gray-900">Recipe Dashboard</h1>
            <p className="text-sm text-gray-500">Manage and cook your recipes</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center space-x-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-full p-1"
              >
                {user?.user_metadata?.avatar_url ? (
                  <img
                    className="h-8 w-8 rounded-full object-cover"
                    src={user.user_metadata.avatar_url}
                    alt={user.user_metadata.full_name || user.email}
                    onError={(e) => {
                      console.log('Error loading avatar:', e)
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-gray-900 flex items-center justify-center">
                    <span className="text-white text-xs font-medium">
                      {user?.user_metadata?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                    </span>
                  </div>
                )}
                <svg
                  className={`h-4 w-4 text-gray-400 transition-transform duration-200 ${
                    isDropdownOpen ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-900 break-words">
                      {user?.user_metadata?.full_name || 'User'}
                    </p>
                    <p className="text-sm text-gray-500">{user?.email}</p>
                  </div>
                  <button
                    onClick={signOut}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Recipe Entry Form - Positioned right under header */}
      <div className="bg-gray-50 border-b border-gray-200 px-6 py-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Add Recipe or Search</h2>
          <RecipeEntryForm onSuccess={handleRecipeSuccess} onSearchResults={handleSearchResults} />
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {renderMainContent()}
      </div>
    </div>
  )
}

export default DashboardPage
