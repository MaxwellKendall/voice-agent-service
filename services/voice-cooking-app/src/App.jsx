import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="text-center mb-8 md:mb-12">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-2 md:mb-4">
            Voice Cooking App
          </h1>
          <p className="text-base md:text-lg lg:text-xl text-gray-600 max-w-2xl mx-auto">
            Hands-free cooking assistant with voice commands
          </p>
        </header>

        <main className="max-w-md md:max-w-2xl lg:max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-md p-6 md:p-8 lg:p-10">
            <h2 className="text-xl md:text-2xl lg:text-3xl font-semibold text-gray-800 mb-4 md:mb-6">
              Welcome to Voice Cooking
            </h2>
            <p className="text-gray-600 mb-6 md:mb-8 text-sm md:text-base lg:text-lg leading-relaxed">
              This is a Progressive Web App that will help you cook hands-free using voice commands. 
              Perfect for when your hands are busy in the kitchen!
            </p>
            
            <div className="space-y-4 md:space-y-6">
              <div className="flex items-center justify-center">
                <button
                  className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 md:py-3 md:px-6 lg:py-4 lg:px-8 rounded-lg transition-colors duration-200 text-sm md:text-base lg:text-lg"
                  onClick={() => setCount((count) => count + 1)}
                >
                  Count is {count}
                </button>
              </div>
              
              <div className="text-xs md:text-sm lg:text-base text-gray-500 text-center">
                Edit <code className="bg-gray-100 px-1 md:px-2 rounded text-xs md:text-sm">src/App.jsx</code> and save to test HMR
              </div>
            </div>
          </div>

          {/* Feature highlights for larger screens */}
          <div className="hidden md:grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-blue-500 text-2xl mb-3">🎤</div>
              <h3 className="font-semibold text-gray-800 mb-2">Voice Commands</h3>
              <p className="text-sm text-gray-600">Control your cooking with natural voice commands</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="text-green-500 text-2xl mb-3">📱</div>
              <h3 className="font-semibold text-gray-800 mb-2">Mobile Optimized</h3>
              <p className="text-sm text-gray-600">Works perfectly on mobile, tablet, and desktop</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 lg:col-span-1">
              <div className="text-purple-500 text-2xl mb-3">🤖</div>
              <h3 className="font-semibold text-gray-800 mb-2">AI Assistant</h3>
              <p className="text-sm text-gray-600">Smart recipe assistance and substitutions</p>
            </div>
          </div>
        </main>

        <footer className="text-center mt-8 md:mt-12 text-gray-500">
          <p className="text-sm md:text-base">Voice Cooking App - Built with React, Vite, and Tailwind CSS</p>
        </footer>
      </div>
    </div>
  )
}

export default App
