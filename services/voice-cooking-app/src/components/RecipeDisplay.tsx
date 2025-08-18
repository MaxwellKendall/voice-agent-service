import React, { JSX } from 'react'
import { RecipeExtractionResponse } from '../services/recipeService'

interface RecipeDisplayProps {
  recipe: RecipeExtractionResponse['data']
  onStartCooking: () => void
  onBack: () => void
}

const RecipeDisplay = ({ recipe, onStartCooking, onBack }: RecipeDisplayProps): JSX.Element | null=> {
  if (!recipe) return null

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 sm:px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-lg sm:text-xl font-bold text-white truncate pr-4">
            {recipe.title}
          </h1>
          <button
            onClick={onBack}
            className="text-white hover:text-blue-100 transition-colors p-2 rounded-full hover:bg-blue-500/20"
            aria-label="Go back to recipe entry"
          >
            <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="p-4 sm:p-6">
        {/* Recipe Image */}
        {recipe.image && (
          <div className="mb-6">
            <img
              src={recipe.image}
              alt={`${recipe.title} - Recipe image`}
              className="w-full h-48 sm:h-64 object-cover rounded-lg shadow-md"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        )}

        {/* Recipe Description */}
        {recipe.description && (
          <div className="mb-6">
            <p className="text-gray-700 leading-relaxed text-sm sm:text-base">{recipe.description}</p>
          </div>
        )}

        {/* Recipe Metadata Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
          {recipe.prepTime && (
            <div className="text-center p-3 bg-blue-50 rounded-lg border border-blue-100">
              <div className="text-xs sm:text-sm text-blue-600 font-medium">Prep Time</div>
              <div className="font-bold text-blue-900 text-sm sm:text-base">{recipe.prepTime}</div>
            </div>
          )}
          {recipe.cookTime && (
            <div className="text-center p-3 bg-green-50 rounded-lg border border-green-100">
              <div className="text-xs sm:text-sm text-green-600 font-medium">Cook Time</div>
              <div className="font-bold text-green-900 text-sm sm:text-base">{recipe.cookTime}</div>
            </div>
          )}
          {recipe.totalTime && (
            <div className="text-center p-3 bg-purple-50 rounded-lg border border-purple-100">
              <div className="text-xs sm:text-sm text-purple-600 font-medium">Total Time</div>
              <div className="font-bold text-purple-900 text-sm sm:text-base">{recipe.totalTime}</div>
            </div>
          )}
          {recipe.servings && (
            <div className="text-center p-3 bg-orange-50 rounded-lg border border-orange-100">
              <div className="text-xs sm:text-sm text-orange-600 font-medium">Servings</div>
              <div className="font-bold text-orange-900 text-sm sm:text-base">{recipe.servings}</div>
            </div>
          )}
        </div>

        {/* Additional Recipe Info */}
        <div className="flex flex-wrap gap-2 mb-6">
          {recipe.cuisine && (
            <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs sm:text-sm rounded-full font-medium">
              {recipe.cuisine}
            </span>
          )}
          {recipe.difficulty && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs sm:text-sm rounded-full font-medium">
              {recipe.difficulty}
            </span>
          )}
        </div>

        {/* Ingredients Section */}
        <div className="mb-8">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center">
            <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              📋
            </span>
            Ingredients
          </h2>
          <div className="bg-gray-50 rounded-lg p-4 sm:p-6">
            <ul className="space-y-3">
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} className="flex items-start">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-700 text-sm sm:text-base leading-relaxed">{ingredient}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Instructions Section */}
        <div className="mb-8">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center">
            <span className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3">
              👨‍🍳
            </span>
            Instructions
          </h2>
          <div className="space-y-4">
            {recipe.instructions.map((instruction, index) => (
              <div key={index} className="flex bg-white border border-gray-200 rounded-lg p-4">
                <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 flex-shrink-0">
                  {index + 1}
                </span>
                <p className="text-gray-700 leading-relaxed text-sm sm:text-base pt-1">{instruction}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Tags Section */}
        {recipe.tags && recipe.tags.length > 0 && (
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {recipe.tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-xs sm:text-sm rounded-full font-medium"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200">
          <button
            onClick={onStartCooking}
            className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white px-6 py-4 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center space-x-3 shadow-lg hover:shadow-xl transform hover:scale-105"
            aria-label="Start cooking with voice assistance"
          >
            <span className="text-xl">🎤</span>
            <span className="text-sm sm:text-base">Enter Cook Mode</span>
          </button>
          <button
            onClick={onBack}
            className="px-6 py-4 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 text-sm sm:text-base"
            aria-label="Add another recipe"
          >
            Add Another Recipe
          </button>
        </div>
      </div>
    </div>
  )
}

export default RecipeDisplay
