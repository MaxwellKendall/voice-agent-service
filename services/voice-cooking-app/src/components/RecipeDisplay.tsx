import React, { JSX, useState, useEffect, useRef } from 'react'
import { RealtimeAgent, RealtimeSession } from '@openai/agents-realtime'
import { allRealtimeTools } from '../tools/realtimeTools'

interface RecipeData {
  id?: string
  title?: string
  description?: string
  ingredients?: string[]
  instructions?: string[]
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
}

interface RecipeDisplayProps {
  recipe: RecipeData
  onBack: () => void
}

const RecipeDisplay = ({ recipe, onBack }: RecipeDisplayProps): JSX.Element | null => {
  const [isCookModeActive, setIsCookModeActive] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ephemeralKey, setEphemeralKey] = useState<string | null>(null)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  
  const sessionRef = useRef<RealtimeSession | null>(null)

  // Generate ephemeral API key
  const generateEphemeralKey = async () => {
    try {
      setError(null)
      const response = await fetch('http://localhost:8000/generate-ephemeral-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`Failed to generate key: ${response.status}`)
      }

      const data = await response.json()
      if (data.success) {
        setEphemeralKey(data.api_key)
        return data.api_key
      } else {
        throw new Error(data.error || 'Failed to generate ephemeral key')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to generate ephemeral key: ${errorMessage}`)
      throw err
    }
  }

  // Initialize and connect to Realtime session
  const connectToRealtime = async () => {
    try {
      // Generate ephemeral key
      const apiKey = ephemeralKey ? ephemeralKey : await generateEphemeralKey()
      
      // Create the cooking assistant agent
      const agent = new RealtimeAgent({
        name: 'Cooking Assistant',
        instructions: `You are a hands-free cooking assistant. Your role is to guide the user step-by-step through cooking a specific recipe.

Recipe Context:
- Recipe ID: ${recipe?.id}
- Recipe Title: ${recipe?.title || 'Unknown'}
- Recipe Description: ${recipe?.description || 'No description available'}

Your Goals:
- Help the user understand and prepare the recipe one step at a time
- Be conversational and adaptive (repeat, clarify, or simplify instructions when asked)
- Track progress through the recipe, remembering which step the user is on
- Offer practical cooking tips (timing cues, substitutions, safety reminders) where useful
- Only reference the current recipe; do not suggest unrelated recipes unless explicitly asked

You have access to tools to search for recipes, get recipe details, and find similar recipes. Use these tools when needed to provide better assistance.

Be concise but helpful. Remember this is a voice conversation, so keep responses natural and conversational.`,
        tools: allRealtimeTools
      })

      // Create the Realtime session
      const session = new RealtimeSession(agent, {
        model: 'gpt-4o-realtime-preview-2025-06-03',
      })

      // Connect to the session
      await session.connect({ apiKey })
      
      sessionRef.current = session
      setIsConnecting(false)

      console.log('Session connected successfully')

    } catch (err) {
      console.error('Failed to connect to Realtime session:', err)
      throw err // Re-throw so the optimistic handler can catch it
    }
  }

  // Disconnect from Realtime session
  const disconnectFromRealtime = async () => {
    try {
      if (sessionRef.current) {
        await sessionRef.current.disconnect()
        sessionRef.current = null
      }
      setIsCookModeActive(false)
      setIsListening(false)
      setIsSpeaking(false)
      setError(null)
    } catch (err) {
      console.error('Error disconnecting from Realtime session:', err)
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (sessionRef.current) {
        disconnectFromRealtime()
      }
    }
  }, [])

  const handleToggleCookMode = async () => {
    if (isCookModeActive) {
      await disconnectFromRealtime()
    } else {
      // Optimistic UI: immediately show as active
      setIsCookModeActive(true)
      setIsConnecting(true)
      setError(null)
      
      // Then attempt connection in background
      try {
        await connectToRealtime()
      } catch (err) {
        // If connection fails, revert optimistic state
        setIsCookModeActive(false)
        setIsConnecting(false)
        console.error('Failed to connect to Realtime session:', err)
        const errorMessage = err instanceof Error ? err.message : 'Unknown error'
        setError(`Failed to connect: ${errorMessage}`)
      }
    }
  }

  if (!recipe) return null

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 max-w-4xl mx-auto">
      {/* Recipe Header */}
      <div className="px-6 py-6 border-b border-gray-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {recipe.title}
            </h1>
            {recipe.description && (
              <p className="text-gray-600 text-base leading-relaxed mb-4">
                {recipe.description}
              </p>
            )}
            
            {/* Recipe Metadata */}
            <div className="flex flex-wrap gap-4 text-sm text-gray-500">
              {recipe.prepTime && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Prep: {recipe.prepTime}
                </span>
              )}
              {recipe.cookTime && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Cook: {recipe.cookTime}
                </span>
              )}
              {recipe.servings && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                  Serves: {recipe.servings}
                </span>
              )}
            </div>
          </div>
          
          <button
            onClick={onBack}
            className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-gray-100 ml-4"
            aria-label="Add another recipe"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Prominent Cook Mode Toggle */}
      <div className={`px-6 py-6 border-b ${
        isCookModeActive 
          ? 'bg-green-50 border-green-200' 
          : 'bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <h3 className={`text-lg font-medium ${
              isCookModeActive ? 'text-green-800' : 'text-gray-900'
            }`}>
              {isCookModeActive ? 'Voice cooking assistant active' : 'Voice cooking assistant'}
            </h3>
            {isConnecting && (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-sm text-blue-600">Connecting...</span>
              </div>
            )}
            {isCookModeActive && !isConnecting && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-green-600">Ready</span>
              </div>
            )}
          </div>
          
          <button
            onClick={handleToggleCookMode}
            disabled={isConnecting}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-200 ${
              isCookModeActive ? 'bg-green-600' : isConnecting ? 'bg-gray-400' : 'bg-gray-200'
            }`}
            aria-label="Toggle cook mode"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                isCookModeActive ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
        
        {error && (
          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
      </div>

      <div className="p-6">
        {/* Recipe Image */}
        {recipe.image && (
          <div className="mb-8">
            <img
              src={recipe.image}
              alt={`${recipe.title} - Recipe image`}
              className="w-full h-64 object-cover rounded-lg shadow-sm"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        )}

        {/* Tags */}
        {(recipe.cuisine || recipe.difficulty || recipe.tags?.length) && (
          <div className="flex flex-wrap gap-2 mb-8">
            {recipe.cuisine && (
              <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
                {recipe.cuisine}
              </span>
            )}
            {recipe.difficulty && (
              <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
                {recipe.difficulty}
              </span>
            )}
            {recipe.tags?.map((tag, index) => (
              <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Ingredients Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <svg className="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Ingredients
          </h2>
          <div className="bg-gray-50 rounded-lg p-4">
            <ul className="space-y-2">
              {recipe.ingredients?.map((ingredient, index) => (
                <li key={index} className="flex items-start">
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-700">{ingredient}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Instructions Section */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <svg className="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Instructions
          </h2>
          <div className="space-y-4">
            {recipe.instructions?.map((instruction, index) => (
              <div key={index} className="flex bg-white border border-gray-200 rounded-lg p-4">
                <span className="w-8 h-8 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-semibold mr-4 flex-shrink-0">
                  {index + 1}
                </span>
                <p className="text-gray-700 leading-relaxed pt-1">{instruction}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default RecipeDisplay
