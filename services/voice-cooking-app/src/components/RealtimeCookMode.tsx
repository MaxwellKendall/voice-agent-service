import React, { useState, useEffect, useRef } from 'react'
import { RealtimeAgent, RealtimeSession } from '@openai/agents-realtime'
import { RecipeExtractionResponse } from '../services/recipeService'
import { allRealtimeTools } from '../tools/realtimeTools'

interface RealtimeCookModeProps {
  recipe: RecipeExtractionResponse['data']
  onExit: () => void
}

const RealtimeCookMode: React.FC<RealtimeCookModeProps> = ({ recipe, onExit }) => {
  const [isConnected, setIsConnected] = useState(false)
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
        tools: allRealtimeTools
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

      console.log('Session connected successfully')

    } catch (err) {
      console.error('Failed to connect to Realtime session:', err)
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      setError(`Failed to connect: ${errorMessage}`)
      setIsConnecting(false)
    }
  }

  // Disconnect from session
  const disconnectFromRealtime = async () => {
    if (sessionRef.current) {
      sessionRef.current = null
      setIsConnected(false)
      setIsListening(false)
      setIsSpeaking(false)
    }
  }

  // Start listening
  const startListening = async () => {
    if (sessionRef.current && isConnected) {
      try {
        // The RealtimeSession handles listening automatically
        setIsListening(true)
      } catch (err) {
        console.error('Failed to start listening:', err)
        setError('Failed to start listening')
      }
    }
  }

  // Stop listening
  const stopListening = async () => {
    if (sessionRef.current && isListening) {
      try {
        // The RealtimeSession handles listening automatically
        setIsListening(false)
      } catch (err) {
        console.error('Failed to stop listening:', err)
        setError('Failed to stop listening')
      }
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnectFromRealtime()
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={onExit}
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-medium text-gray-900">Voice Cooking Assistant</h1>
              <p className="text-sm text-gray-500">Hands-free recipe guidance</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-300'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
        {/* Recipe Info */}
        <div className="max-w-md w-full mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-2">
              {recipe?.title || 'Recipe'}
            </h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              {recipe?.description || 'No description available'}
            </p>
          </div>
        </div>

        {/* Connection Status */}
        {!isConnected && !isConnecting && (
          <div className="max-w-md w-full mb-6">
            <button
              onClick={connectToRealtime}
              className="w-full bg-gray-900 text-white py-3 px-6 rounded-lg font-medium hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
            >
              Connect to Assistant
            </button>
          </div>
        )}

        {/* Connecting State */}
        {isConnecting && (
          <div className="max-w-md w-full mb-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
              <p className="text-gray-600">Connecting to assistant...</p>
            </div>
          </div>
        )}

        {/* Connected State */}
        {isConnected && (
          <div className="max-w-md w-full">
            {/* Voice Controls */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
              <div className="flex items-center justify-center space-x-4">
                <button
                  onClick={isListening ? stopListening : startListening}
                  disabled={isSpeaking}
                  className={`flex items-center justify-center w-16 h-16 rounded-full transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                    isListening
                      ? 'bg-red-500 hover:bg-red-600 focus:ring-red-500'
                      : 'bg-gray-900 hover:bg-gray-800 focus:ring-gray-900'
                  } ${isSpeaking ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {isListening ? (
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                    </svg>
                  ) : (
                    <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                      <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                    </svg>
                  )}
                </button>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-900">
                    {isListening ? 'Listening...' : isSpeaking ? 'Assistant speaking...' : 'Tap to speak'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {isListening ? 'Tap to stop' : 'Ask for cooking guidance'}
                  </p>
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="text-sm font-medium text-blue-900 mb-2">How to use</h3>
              <ul className="text-xs text-blue-800 space-y-1">
                <li>• Tap the microphone to start speaking</li>
                <li>• Ask questions about ingredients, steps, or timing</li>
                <li>• Request clarification or repeat instructions</li>
                <li>• The assistant will guide you through the recipe</li>
              </ul>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="max-w-md w-full mt-6">
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
          </div>
        )}
      </div>
    </div>
  )
}

export default RealtimeCookMode
