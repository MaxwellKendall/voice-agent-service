import { RecipeExtractionResponse } from '../services/recipeService'

interface RecipeDisplayProps {
  recipe: RecipeExtractionResponse['data']
  onStartCooking: () => void
  onBack: () => void
}

const RecipeDisplay = ({ recipe, onStartCooking, onBack }: RecipeDisplayProps): JSX.Element => {
  if (!recipe) return null

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white">{recipe.title}</h2>
          <button
            onClick={onBack}
            className="text-white hover:text-blue-100 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Recipe Image */}
        {recipe.image && (
          <div className="mb-6">
            <img
              src={recipe.image}
              alt={recipe.title}
              className="w-full h-48 object-cover rounded-lg"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        )}

        {/* Recipe Description */}
        {recipe.description && (
          <div className="mb-6">
            <p className="text-gray-600 leading-relaxed">{recipe.description}</p>
          </div>
        )}

        {/* Recipe Metadata */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {recipe.prepTime && (
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Prep Time</div>
              <div className="font-semibold text-gray-900">{recipe.prepTime}</div>
            </div>
          )}
          {recipe.cookTime && (
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Cook Time</div>
              <div className="font-semibold text-gray-900">{recipe.cookTime}</div>
            </div>
          )}
          {recipe.totalTime && (
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Total Time</div>
              <div className="font-semibold text-gray-900">{recipe.totalTime}</div>
            </div>
          )}
          {recipe.servings && (
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-500">Servings</div>
              <div className="font-semibold text-gray-900">{recipe.servings}</div>
            </div>
          )}
        </div>

        {/* Ingredients */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Ingredients</h3>
          <ul className="space-y-2">
            {recipe.ingredients.map((ingredient, index) => (
              <li key={index} className="flex items-start">
                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                <span className="text-gray-700">{ingredient}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Instructions */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Instructions</h3>
          <ol className="space-y-4">
            {recipe.instructions.map((instruction, index) => (
              <li key={index} className="flex">
                <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-semibold mr-3 flex-shrink-0">
                  {index + 1}
                </span>
                <span className="text-gray-700 leading-relaxed">{instruction}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Tags */}
        {recipe.tags && recipe.tags.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {recipe.tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200">
          <button
            onClick={onStartCooking}
            className="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors duration-200 flex items-center justify-center space-x-2"
          >
            <span>🎤</span>
            <span>Start Cooking with Voice</span>
          </button>
          <button
            onClick={onBack}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors duration-200"
          >
            Add Another Recipe
          </button>
        </div>
      </div>
    </div>
  )
}

export default RecipeDisplay
