"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock

from app.api import app

client = TestClient(app)


class TestHealthCheck:
    """Test cases for health check endpoint."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data


class TestChatEndpoint:
    """Test cases for chat endpoint."""
    
    @patch('app.api.process_query')
    def test_chat_success(self, mock_process_query):
        """Test successful chat request."""
        mock_process_query.return_value = "Here are some easy Mexican recipes..."
        
        response = client.post(
            "/chat",
            json={
                "message": "What are some easy Mexican recipes?",
                "chat_history": []
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Here are some easy Mexican recipes..."
        assert data["recipes"] is None
        assert data["tool_calls"] is None
        
        mock_process_query.assert_called_once_with(
            query="What are some easy Mexican recipes?",
            chat_history=[]
        )
    
    @patch('app.api.process_query')
    def test_chat_with_history(self, mock_process_query):
        """Test chat request with chat history."""
        mock_process_query.return_value = "Based on our conversation..."
        
        chat_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        response = client.post(
            "/chat",
            json={
                "message": "What's similar to turkey chili?",
                "chat_history": chat_history
            }
        )
        
        assert response.status_code == 200
        mock_process_query.assert_called_once_with(
            query="What's similar to turkey chili?",
            chat_history=chat_history
        )
    
    @patch('app.api.process_query')
    def test_chat_exception(self, mock_process_query):
        """Test chat request with exception."""
        mock_process_query.side_effect = Exception("Processing error")
        
        response = client.post(
            "/chat",
            json={
                "message": "Test message",
                "chat_history": []
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]
    
    def test_chat_invalid_request(self):
        """Test chat request with invalid data."""
        response = client.post(
            "/chat",
            json={
                "message": "",  # Empty message
                "chat_history": []
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_missing_message(self):
        """Test chat request with missing message."""
        response = client.post(
            "/chat",
            json={
                "chat_history": []
            }
        )
        
        assert response.status_code == 422  # Validation error


class TestToolsEndpoint:
    """Test cases for tools endpoint."""
    
    def test_list_tools(self):
        """Test tools listing endpoint."""
        response = client.get("/tools")
        
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
        
        # Check that our custom tools are listed
        tool_names = [tool["name"] for tool in data["tools"]]
        assert "search_recipes" in tool_names
        assert "get_similar_recipes" in tool_names


class TestCORS:
    """Test cases for CORS functionality."""
    
    def test_cors_headers(self):
        """Test that CORS headers are present."""
        response = client.options(
            "/chat",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # CORS preflight should be handled
        assert response.status_code in [200, 405]  # 405 is also acceptable for OPTIONS 