"""Unit tests for custom tools."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from app.tools import search_recipes, get_similar_recipes, get_embeddings
from app.vector_store import RecipeVectorStore


class MockQdrantClient:
    """Mock Qdrant client for testing."""
    
    def __init__(self):
        self.collections = Mock()
        self.collections.collections = [Mock(name="recipes")]
        
    def get_collections(self):
        return self.collections
    
    def search(self, collection_name, query_vector, limit):
        # Mock search results
        mock_result = Mock()
        mock_result.id = "test_recipe_1"
        mock_result.payload = {
            "title": "Test Recipe",
            "summary": "A delicious test recipe",
            "url": "https://example.com/recipe"
        }
        mock_result.score = 0.95
        return [mock_result]
    
    def retrieve(self, collection_name, ids):
        # Mock retrieve result
        mock_point = Mock()
        mock_point.id = "test_recipe_1"
        mock_point.payload = {
            "title": "Test Recipe",
            "summary": "A delicious test recipe",
            "url": "https://example.com/recipe"
        }
        mock_point.vector = [0.1] * 1536  # Mock vector
        return [mock_point]


@pytest.fixture
def mock_vector_store():
    """Fixture for mocked vector store."""
    with patch('app.tools.get_vector_store') as mock_get_store:
        mock_store = Mock(spec=RecipeVectorStore)
        mock_get_store.return_value = mock_store
        yield mock_store


@pytest.fixture
def mock_embeddings():
    """Fixture for mocked embeddings."""
    with patch('app.tools.get_embeddings') as mock_get_embeddings:
        mock_emb = Mock()
        mock_emb.embed_query.return_value = [0.1] * 1536
        mock_get_embeddings.return_value = mock_emb
        yield mock_emb


class TestSearchRecipes:
    """Test cases for search_recipes tool."""
    
    def test_search_recipes_success(self, mock_vector_store, mock_embeddings):
        """Test successful recipe search."""
        # Mock search results
        mock_recipes = [
            {
                "id": "recipe_1",
                "title": "Mexican Tacos",
                "summary": "Delicious homemade tacos",
                "url": "https://example.com/tacos",
                "score": 0.95
            }
        ]
        mock_vector_store.search_recipes.return_value = mock_recipes
        
        # Test the function
        result = search_recipes("easy Mexican recipes")
        
        # Verify results
        assert len(result) == 1
        assert result[0]["title"] == "Mexican Tacos"
        assert result[0]["id"] == "recipe_1"
        
        # Verify calls
        mock_embeddings.embed_query.assert_called_once_with("easy Mexican recipes")
        mock_vector_store.search_recipes.assert_called_once()
    
    def test_search_recipes_empty_result(self, mock_vector_store, mock_embeddings):
        """Test search with no results."""
        mock_vector_store.search_recipes.return_value = []
        
        result = search_recipes("nonexistent recipe")
        
        assert result == []
    
    def test_search_recipes_exception(self, mock_vector_store, mock_embeddings):
        """Test search with exception handling."""
        mock_vector_store.search_recipes.side_effect = Exception("Database error")
        
        result = search_recipes("test query")
        
        assert result == []


class TestGetSimilarRecipes:
    """Test cases for get_similar_recipes tool."""
    
    def test_get_similar_recipes_success(self, mock_vector_store):
        """Test successful similar recipe search."""
        # Mock similar recipes
        mock_similar = [
            {
                "id": "recipe_2",
                "title": "Beef Chili",
                "summary": "Classic beef chili",
                "url": "https://example.com/beef-chili",
                "score": 0.88
            }
        ]
        mock_vector_store.get_similar_recipes.return_value = mock_similar
        
        # Test the function
        result = get_similar_recipes("recipe_1")
        
        # Verify results
        assert len(result) == 1
        assert result[0]["title"] == "Beef Chili"
        
        # Verify calls
        mock_vector_store.get_similar_recipes.assert_called_once_with("recipe_1", limit=5)
    
    def test_get_similar_recipes_recipe_not_found(self, mock_vector_store):
        """Test similar search when recipe doesn't exist."""
        mock_vector_store.get_recipe_by_id.return_value = None
        
        result = get_similar_recipes("nonexistent_recipe")
        
        assert result == []
    
    def test_get_similar_recipes_no_vector(self, mock_vector_store):
        """Test similar search when recipe has no vector."""
        mock_recipe = {
            "id": "recipe_1",
            "title": "Test Recipe",
            "summary": "Test summary",
            "url": "https://example.com/recipe"
            # No vector field
        }
        mock_vector_store.get_recipe_by_id.return_value = mock_recipe
        
        result = get_similar_recipes("recipe_1")
        
        assert result == []
    
    def test_get_similar_recipes_exception(self, mock_vector_store):
        """Test similar search with exception handling."""
        mock_vector_store.get_recipe_by_id.side_effect = Exception("Database error")
        
        result = get_similar_recipes("recipe_1")
        
        assert result == []


class TestEmbeddings:
    """Test cases for embeddings functionality."""
    
    @patch('app.tools.OpenAIEmbeddings')
    def test_get_embeddings_creation(self, mock_embeddings_class):
        """Test embeddings instance creation."""
        mock_instance = Mock()
        mock_embeddings_class.return_value = mock_instance
        
        # Reset the global instance
        import app.tools
        app.tools._embeddings = None
        
        with patch('app.config.get_openai_api_key', return_value="test_key"):
            result = get_embeddings()
            
            assert result == mock_instance
            mock_embeddings_class.assert_called_once_with(openai_api_key="test_key")
    
    def test_get_embeddings_singleton(self):
        """Test that embeddings instance is reused."""
        # Reset the global instance
        import app.tools
        app.tools._embeddings = None
        
        with patch('app.tools.OpenAIEmbeddings') as mock_embeddings_class:
            mock_instance = Mock()
            mock_embeddings_class.return_value = mock_instance
            
            with patch('app.config.get_openai_api_key', return_value="test_key"):
                # First call
                result1 = get_embeddings()
                # Second call
                result2 = get_embeddings()
                
                assert result1 == result2
                assert result1 == mock_instance
                # Should only create one instance
                mock_embeddings_class.assert_called_once() 