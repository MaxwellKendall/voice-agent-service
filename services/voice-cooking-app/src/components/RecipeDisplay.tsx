import React, { JSX } from 'react'

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
  onStartCooking: () => void
  onStartRealtimeCooking: () => void
  onBack: () => void
}

const RecipeDisplay = ({ recipe, onStartCooking, onStartRealtimeCooking, onBack }: RecipeDisplayProps): JSX.Element | null => {
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

        {/* Action Buttons */}
        <div className="border-t border-gray-200 pt-6">
          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={onStartCooking}
              className="flex-1 bg-gray-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
            >
              Start Cooking with Voice Assistant
            </button>
            <button
              onClick={onStartRealtimeCooking}
              className="flex-1 border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2"
            >
              Real-time Cooking Mode
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RecipeDisplay
