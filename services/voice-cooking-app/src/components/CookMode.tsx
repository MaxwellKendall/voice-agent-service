import React, { useState, useEffect, useRef } from 'react'
import { RecipeExtractionResponse } from '../services/recipeService'

interface CookModeProps {
  recipe: RecipeExtractionResponse['data']
  onExit: () => void
}

interface WebSocketMessage {
  type: 'text' | 'audio_transcription' | 'response' | 'error' | 'system' | 'typing' | 'ping' | 'pong'
  content?: string
  status?: string
  timestamp?: number
  recipe_id?: string
  audio?: string  // Base64 encoded audio data
}

const WS_URL = import.meta.env.VITE_COOKING_ASSISTANT_WS_URL || 'ws://localhost:8001/ws/cooking-assistant';

const CookMode: React.FC<CookModeProps> = ({ recipe, onExit }) => {
  const [isConnected, setIsConnected] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [assistantResponse, setAssistantResponse] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [microphonePermission, setMicrophonePermission] = useState<'granted' | 'denied' | 'prompt' | 'unknown'>('unknown')
  
  const websocketRef = useRef<WebSocket | null>(null)
  const recognitionRef = useRef<SpeechRecognition | null>(null)
  const clientId = useRef(`client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)

  // Request microphone permission
  const requestMicrophonePermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      setMicrophonePermission('granted')
      // Stop the stream immediately since we just needed permission
      stream.getTracks().forEach(track => track.stop())
      return true
    } catch (err) {
      console.error('Microphone permission denied:', err)
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setMicrophonePermission('denied')
          setError('Microphone access was denied. Please allow microphone access in your browser settings.')
        } else if (err.name === 'NotFoundError') {
          setError('No microphone found. Please connect a microphone and try again.')
        } else {
          setError(`Microphone error: ${err.message}`)
        }
      }
      return false
    }
  }

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        // Connect to cooking assistant server using environment variable
        const ws = new WebSocket(`${WS_URL}/${clientId.current}`);
        
        ws.onopen = () => {
          console.log('WebSocket connected')
          setIsConnected(true)
          setError(null)
        }
        
        ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            handleWebSocketMessage(message)
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err)
          }
        }
        
        ws.onclose = () => {
          console.log('WebSocket disconnected')
          setIsConnected(false)
          setIsListening(false)
        }
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          setError('Failed to connect to cooking assistant')
          setIsConnected(false)
        }
        
        websocketRef.current = ws
      } catch (err) {
        console.error('Failed to create WebSocket:', err)
        setError('Failed to connect to cooking assistant')
      }
    }

    connectWebSocket()

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close()
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop()
      }
    }
  }, [])

  // Initialize speech recognition after permission is granted
  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognition = new SpeechRecognition()
      
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'
      
      recognition.onstart = () => {
        console.log('Speech recognition started')
        setIsListening(true)
        setError(null)
      }
      
      recognition.onresult = (event) => {
        let finalTranscript = ''
        let interimTranscript = ''
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalTranscript += transcript
          } else {
            interimTranscript += transcript
          }
        }
        
        setTranscript(finalTranscript + interimTranscript)
      }
      
      recognition.onend = () => {
        console.log('Speech recognition ended')
        setIsListening(false)
        
        // Send final transcript if we have one
        if (transcript.trim()) {
          sendMessage({
            type: 'audio_transcription',
            content: transcript.trim(),
            recipe_id: recipe?.id
          })
          setTranscript('')
        }
      }
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        setError(`Speech recognition error: ${event.error}`)
      }
      
      recognitionRef.current = recognition
      return true
    } else {
      setError('Speech recognition not supported in this browser')
      return false
    }
  }

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'response':
        setAssistantResponse(message.content || '')
        setIsTyping(false)
        
        // Play audio if provided
        if (message.audio) {
          playAudio(message.audio)
        }
        break
      case 'typing':
        setIsTyping(message.status === 'started')
        break
      case 'error':
        setError(message.content || 'An error occurred')
        break
      case 'system':
        console.log('System message:', message.content)
        break
      case 'ping':
        // Respond to ping with pong
        sendMessage({ type: 'pong' })
        break
      default:
        console.log('Unknown message type:', message.type)
    }
  }

  const playAudio = (audioBase64: string) => {
    try {
      // Convert base64 to audio blob
      const audioData = atob(audioBase64)
      const audioArray = new Uint8Array(audioData.length)
      for (let i = 0; i < audioData.length; i++) {
        audioArray[i] = audioData.charCodeAt(i)
      }
      
      const audioBlob = new Blob([audioArray], { type: 'audio/mpeg' })
      const audioUrl = URL.createObjectURL(audioBlob)
      
      // Create and play audio
      const audio = new Audio(audioUrl)
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl) // Clean up
      }
      audio.onerror = (error) => {
        console.error('Audio playback error:', error)
        URL.revokeObjectURL(audioUrl) // Clean up
      }
      
      audio.play().catch(error => {
        console.error('Failed to play audio:', error)
        URL.revokeObjectURL(audioUrl) // Clean up
      })
    } catch (error) {
      console.error('Error processing audio data:', error)
    }
  }

  const sendMessage = (message: Partial<WebSocketMessage>) => {
    if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify(message))
    } else {
      setError('Not connected to cooking assistant')
    }
  }

  const startListening = async () => {
    if (!isConnected) {
      setError('Not connected to cooking assistant')
      return
    }

    // Check if we already have permission
    if (microphonePermission === 'granted') {
      if (recognitionRef.current && !isListening) {
        recognitionRef.current.start()
      }
      return
    }

    // Request permission first
    const permissionGranted = await requestMicrophonePermission()
    if (permissionGranted) {
      // Initialize speech recognition after permission is granted
      const recognitionInitialized = initializeSpeechRecognition()
      if (recognitionInitialized && recognitionRef.current) {
        recognitionRef.current.start()
      }
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
    }
  }

  const sendTextMessage = () => {
    if (transcript.trim()) {
      sendMessage({
        type: 'text',
        content: transcript.trim(),
        recipe_id: recipe?.id
      })
      setTranscript('')
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <h2 className="text-xl font-bold text-white">Cook Mode</h2>
          </div>
          <button
            onClick={onExit}
            className="text-white hover:text-green-100 transition-colors p-2 rounded-full hover:bg-green-500/20"
            aria-label="Exit cook mode"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Recipe Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">Cooking: {recipe?.title || 'Unknown Recipe'}</h3>
            <p className="text-sm text-gray-600">Ask me anything about this recipe!</p>
          </div>

          {/* Connection Status */}
          {!isConnected && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-yellow-800">Connecting to cooking assistant...</span>
              </div>
            </div>
          )}

          {/* Microphone Permission Status */}
          {isConnected && microphonePermission === 'denied' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-red-800">Microphone access denied. Please allow microphone access in your browser settings.</span>
              </div>
            </div>
          )}

          {isConnected && microphonePermission === 'granted' && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-green-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-green-800">Microphone access granted. You can now use voice commands!</span>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-red-800">{error}</span>
              </div>
            </div>
          )}

          {/* Microphone Controls */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={isListening ? stopListening : startListening}
              disabled={!isConnected || microphonePermission === 'denied'}
              className={`flex-1 px-6 py-4 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center space-x-3 ${
                isListening
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : microphonePermission === 'denied'
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-500 hover:bg-blue-600 text-white disabled:bg-gray-300 disabled:cursor-not-allowed'
              }`}
            >
              <span className="text-xl">
                {isListening ? '🔴' : microphonePermission === 'denied' ? '🚫' : '🎤'}
              </span>
              <span>
                {isListening 
                  ? 'Stop Listening' 
                  : microphonePermission === 'denied'
                  ? 'Microphone Denied'
                  : 'Start Listening'
                }
              </span>
            </button>
            
            <button
              onClick={sendTextMessage}
              disabled={!isConnected || !transcript.trim()}
              className="px-6 py-4 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition-all duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Send Text
            </button>
          </div>

          {/* Transcript Display */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Your Message:</label>
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Speak or type your question..."
              className="w-full p-3 border border-gray-300 rounded-lg resize-none h-24 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={!isConnected}
            />
          </div>

          {/* Assistant Response */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Cooking Assistant:</label>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 min-h-[100px]">
              {isTyping ? (
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-blue-700">Assistant is typing...</span>
                </div>
              ) : assistantResponse ? (
                <p className="text-gray-800 leading-relaxed">{assistantResponse}</p>
              ) : (
                <p className="text-gray-500 italic">Ask me anything about cooking this recipe!</p>
              )}
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">How to use:</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Click "Start Listening" and speak your question</li>
              <li>• Or type your question and click "Send Text"</li>
              <li>• Ask about ingredients, techniques, or cooking tips</li>
              <li>• I'll help you cook this recipe step by step!</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CookMode
