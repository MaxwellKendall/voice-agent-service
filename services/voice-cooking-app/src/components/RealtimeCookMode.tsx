import React, { useState, useEffect, useRef } from 'react'
import { RealtimeAgent, RealtimeSession, tool } from '@openai/agents-realtime'
import { RecipeExtractionResponse } from '../services/recipeService'
import { z } from 'zod'
import { findSimilarRecipesFromUrlTool, getRecipeByIdTool, getSimilarRecipesTool, searchRecipesTool } from '../tools/realtimeTools'

interface RealtimeCookModeProps {
  recipe: RecipeExtractionResponse['data']
  onExit: () => void
}

const RealtimeCookMode: React.FC<RealtimeCookModeProps> = ({ recipe, onExit }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ephemeralKey, setEphemeralKey] = useState<string | null>(null)
  
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
      setIsConnecting(true)
      setError(null)

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
            tools: [searchRecipesTool, getRecipeByIdTool, getSimilarRecipesTool, findSimilarRecipesFromUrlTool]
          })

      // Create the Realtime session
      const session = new RealtimeSession(agent, {
        model: 'gpt-4o-realtime-preview-2025-06-03',
      })

      // Connect to the session
      await session.connect({ apiKey })
      
      sessionRef.current = session
      setIsConnected(true)
      setIsConnecting(false)

      // Handle session events - simplified for now
      console.log('Session connected successfully')

    } catch (err) {
      console.error('Failed to connect to Realtime session:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to connect: ${errorMessage}`)
      setIsConnecting(false)
    }
  }

  // Disconnect from session
  const disconnect = async () => {
    if (sessionRef.current) {
      try {
        // Close the session - the exact method may vary based on the API
        // For now, we'll just set the ref to null
        sessionRef.current = null
      } catch (err) {
        console.error('Error disconnecting:', err)
      }
    }
    setIsConnected(false)
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [])

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Voice Cooking Assistant</h2>
        <button
          onClick={onExit}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
        >
          Exit Cook Mode
        </button>
      </div>

      {/* Recipe Info */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">Current Recipe</h3>
        <p className="text-blue-700">
          <strong>Title:</strong> {recipe?.title || 'Unknown'}
        </p>
        <p className="text-blue-700">
          <strong>ID:</strong> {recipe?.id || 'Unknown'}
        </p>
      </div>

      {/* Connection Status */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : isConnecting ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
          <span className="text-sm font-medium">
            {isConnected ? 'Connected' : isConnecting ? 'Connecting...' : 'Disconnected'}
          </span>
        </div>

        {!isConnected && !isConnecting && (
          <button
            onClick={connectToRealtime}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Voice Assistant
          </button>
        )}

        {isConnected && (
          <button
            onClick={disconnect}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Stop Voice Assistant
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">How to Use</h3>
        <ul className="text-gray-700 space-y-1">
          <li>• Click "Start Voice Assistant" to begin</li>
          <li>• Grant microphone access when prompted</li>
          <li>• Speak naturally to ask questions about the recipe</li>
          <li>• The assistant will respond with voice and can help with cooking steps</li>
          <li>• You can interrupt the assistant at any time</li>
        </ul>
      </div>
    </div>
  )
}

export default RealtimeCookMode
