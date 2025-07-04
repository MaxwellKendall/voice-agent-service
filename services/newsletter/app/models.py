"""Pydantic models for API requests and responses."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="The user's message")
    chat_id: Optional[str] = Field(
        default=None, 
        description="Chat ID to continue conversation. If null, creates a new chat."
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
    chat_id: str = Field(..., description="The chat ID (new or existing)")
    recipes: Optional[List[RecipeInfo]] = Field(
        default=None, 
        description="Any recipes found during the conversation"
    )
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Information about tools that were called"
    )

class ChatInfo(BaseModel):
    """Model for chat information."""
    id: str = Field(..., description="Chat unique identifier")
    title: str = Field(..., description="Chat title")
    created_at: datetime = Field(..., description="Chat creation timestamp")
    updated_at: datetime = Field(..., description="Chat last update timestamp")
    message_count: int = Field(..., description="Number of messages in the chat")

class ChatListResponse(BaseModel):
    """Response model for chat list endpoint."""
    chats: List[ChatInfo] = Field(..., description="List of all chats")

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp") 