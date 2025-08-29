import React from 'react'

interface RecipeCardProps {
  recipe: {
    id?: string
    title: string
    image?: string
    summary?: string
    description?: string
    tags?: string[]
    cuisine?: string
    category?: string
    prepTime?: string
    cookTime?: string
    servings?: string[]
    rating?: number
    ratingCount?: number
  }
  onClick?: () => void
  className?: string
}

const RecipeCard: React.FC<RecipeCardProps> = ({
  recipe,
  onClick,
  className = ""
}) => {
    console.log('helllooo world....', recipe)
  const handleClick = () => {
    if (onClick) {
      onClick()
    }
  }

  const getPreviewText = () => {
    return recipe.summary || recipe.description || "No description available"
  }

  const truncateText = (text: string, maxLength: number = 120) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength).trim() + '...'
  }

  const formatTime = (time: string | undefined) => {
    if (!time) return null
    if (time === '--') return null
    return time
  }

  const getTags = () => {
    const tags = []
    if (recipe.cuisine) tags.push(recipe.cuisine)
    if (recipe.category) tags.push(recipe.category)
    if (recipe.tags) tags.push(...recipe.tags)
    return tags.slice(0, 3) // Limit to 3 tags
  }

  return (
    <div
      className={`
        bg-white rounded-lg shadow-sm border border-gray-200 
        overflow-hidden transition-all duration-200 
        hover:shadow-md hover:border-gray-300 
        cursor-pointer group
        ${className}
      `}
      onClick={handleClick}
    >
      {/* Recipe Image */}
      <div className="relative h-48 bg-gray-100 overflow-hidden">
        {recipe.image ? (
          <img
            src={recipe.image}
            alt={recipe.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
              e.currentTarget.nextElementSibling?.classList.remove('hidden')
            }}
          />
        ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
          <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        )}
        {/* Rating Badge */}
        {recipe.rating && recipe.rating > 0 && (
          <div className="absolute top-3 right-3 bg-white bg-opacity-90 rounded-full px-2 py-1 flex items-center space-x-1">
            <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="text-sm font-medium text-gray-700">
              {recipe.rating.toFixed(1)}
            </span>
          </div>
        )}
      </div>

      {/* Recipe Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors duration-200">
          {recipe.title}
        </h3>

        {/* Tags */}
        {getTags().length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {getTags().map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Preview Text */}
        <p className="text-sm text-gray-600 mb-3 line-clamp-3">
          {truncateText(getPreviewText())}
        </p>

        {/* Recipe Meta */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            {formatTime(recipe.prepTime) && (
              <div className="flex items-center space-x-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Prep: {formatTime(recipe.prepTime)}</span>
              </div>
            )}
            {formatTime(recipe.cookTime) && (
              <div className="flex items-center space-x-1">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Cook: {formatTime(recipe.cookTime)}</span>
              </div>
            )}
          </div>
          
          {recipe.servings && recipe.servings.length > 0 && (
            <div className="flex items-center space-x-1">
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span>{recipe.servings[0]}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default RecipeCard
