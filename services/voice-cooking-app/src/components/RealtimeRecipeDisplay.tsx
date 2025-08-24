import React from 'react'
import { RecipeExtractionResponse } from '../services/recipeService'

interface RealtimeRecipeDisplayProps {
  recipe: RecipeExtractionResponse['data']
}

const RealtimeRecipeDisplay: React.FC<RealtimeRecipeDisplayProps> = ({ recipe }) => {
  if (!recipe) return null

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Recipe Image */}
      {recipe.image && (
        <div className="relative h-64 bg-gray-100">
          <img
            src={recipe.image}
            alt={recipe.title || 'Recipe'}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        </div>
      )}

      <div className="p-6">
        {/* Recipe Title */}
        <h1 className="text-2xl font-medium text-gray-900 mb-3">
          {recipe.title || 'Untitled Recipe'}
        </h1>

        {/* Recipe Description */}
        {recipe.description && (
          <p className="text-gray-600 leading-relaxed mb-6">
            {recipe.description}
          </p>
        )}

        {/* Recipe Metadata */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {recipe.prepTime && (
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Prep Time</div>
              <div className="text-sm font-medium text-gray-900">{recipe.prepTime}</div>
            </div>
          )}
          {recipe.cookTime && (
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Cook Time</div>
              <div className="text-sm font-medium text-gray-900">{recipe.cookTime}</div>
            </div>
          )}
          {recipe.totalTime && (
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Total Time</div>
              <div className="text-sm font-medium text-gray-900">{recipe.totalTime}</div>
            </div>
          )}
          {recipe.servings && (
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Servings</div>
              <div className="text-sm font-medium text-gray-900">{recipe.servings}</div>
            </div>
          )}
        </div>

        {/* Recipe Tags */}
        <div className="flex flex-wrap gap-2 mb-8">
          {recipe.cuisine && (
            <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full font-medium">
              {recipe.cuisine}
            </span>
          )}
          {recipe.difficulty && (
            <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full font-medium">
              {recipe.difficulty}
            </span>
          )}
        </div>

        {/* Ingredients Section */}
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Ingredients</h2>
          {recipe.ingredients && recipe.ingredients.length > 0 ? (
            <ul className="space-y-2">
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} className="flex items-start">
                  <span className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-700">{ingredient}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 italic">No ingredients listed</p>
          )}
        </div>

        {/* Instructions Section */}
        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">Instructions</h2>
          {recipe.instructions && recipe.instructions.length > 0 ? (
            <ol className="space-y-4">
              {recipe.instructions.map((instruction, index) => (
                <li key={index} className="flex">
                  <span className="flex-shrink-0 w-6 h-6 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-medium mr-3">
                    {index + 1}
                  </span>
                  <span className="text-gray-700 leading-relaxed">{instruction}</span>
                </li>
              ))}
            </ol>
          ) : (
            <p className="text-gray-500 italic">No instructions available</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default RealtimeRecipeDisplay
