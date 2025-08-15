import React, { JSX } from 'react'
import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'

const DashboardPage = (): JSX.Element => {
  const { user, signOut } = useAuth()
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const handleSignOut = async (): Promise<void> => {
    try {
      await signOut()
    } catch (error) {
      console.error('Sign out error:', error)
    }
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">
                  Voice Cooking App
                </h1>
              </div>
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
                    <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
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
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50">
                    <div className="py-1">
                      {/* User Info */}
                      <div className="px-4 py-2 border-b border-gray-100">
                        <p className="text-sm font-medium text-gray-900">
                          {user?.user_metadata?.full_name || 'User'}
                        </p>
                        <p className="text-xs text-gray-500 truncate">
                          {user?.email}
                        </p>
                      </div>
                      
                      {/* Sign Out Button */}
                      <button
                        onClick={handleSignOut}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 focus:outline-none focus:bg-red-50 transition-colors duration-150"
                      >
                        Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="py-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Welcome to Voice Cooking!
              </h2>
              <p className="text-gray-600 mb-6">
                You're now signed in and ready to start cooking hands-free. 
                Paste a recipe URL to get started with voice-guided cooking.
              </p>

              {/* Recipe Entry Section */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Get Started
                </h3>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="recipe-url" className="block text-sm font-medium text-gray-700 mb-2">
                      Recipe URL
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="url"
                        id="recipe-url"
                        placeholder="https://example.com/recipe"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      />
                      <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200">
                        Extract Recipe
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* User Info */}
              <div className="border-t pt-6 mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Account Information
                </h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Email</dt>
                      <dd className="text-sm text-gray-900">{user?.email}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Name</dt>
                      <dd className="text-sm text-gray-900">
                        {user?.user_metadata?.full_name || 'Not provided'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">User ID</dt>
                      <dd className="text-sm text-gray-900 font-mono">{user?.id}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Provider</dt>
                      <dd className="text-sm text-gray-900 capitalize">
                        {user?.app_metadata?.provider || 'Unknown'}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
