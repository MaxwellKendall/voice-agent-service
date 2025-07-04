"""Pydantic models for API requests and responses."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="The user's message")
    chat_history: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="Optional chat history for context"
    )

class RecipeInfo(BaseModel):
    """Model for recipe information."""
    id: str = Field(..., description="Recipe unique identifier")
    title: str = Field(..., description="Recipe title")
    summary: str = Field(..., description="Recipe summary")
    url: str = Field(..., description="Recipe URL")
    score: Optional[float] = Field(None, description="Relevance or similarity score")

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="The AI agent's response")
    recipes: Optional[List[RecipeInfo]] = Field(
        default=None, 
        description="Any recipes found during the conversation"
    )
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Information about tools that were called"
    )

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp") 