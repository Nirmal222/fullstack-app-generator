"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class CodeGenerationRequest(BaseModel):
    """Request model for code generation"""
    prompt: str
    framework: str = "react"
    session_id: Optional[str] = None


class SessionResponse(BaseModel):
    """Response model for session information"""
    session_id: str
    user_id: str
    state: Dict[str, Any]
    created_at: str


class SessionListResponse(BaseModel):
    """Response model for session list"""
    sessions: List[SessionResponse]
    total: int
    page: int
    page_size: int


class ClearSessionRequest(BaseModel):
    """Request model for clearing a session"""
    session_id: str


class ErrorResponse(BaseModel):
    """Standard error response"""
    type: str = "error"
    message: str
    details: Optional[Dict[str, Any]] = None
