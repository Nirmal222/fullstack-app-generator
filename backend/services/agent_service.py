"""
Agent service for managing ADK sessions and runners
Based on bytecourse-service patterns
"""

from typing import Optional, AsyncGenerator, Dict, Any
from google.adk.sessions import Session
from google.adk.runners import Runner
from google.genai import types
import json

from db import get_session_service
from utils.config import Config


async def get_user_session(
    user_id: str,
    session_id: Optional[str] = None,
    app_name: str = None
) -> Session:
    """
    Get or create a session for a user
    
    Args:
        user_id: User identifier
        session_id: Optional existing session ID
        app_name: Application name
    
    Returns:
        Session object
    """
    session_service = get_session_service()
    app_name = app_name or Config.APP_NAME
    
    if session_id:
        # Try to get existing session
        try:
            session = await session_service.get_session(
                user_id=user_id,
                session_id=session_id
            )
            if session:
                return session
        except Exception:
            pass  # Create new session if get fails
    
    # Create new session
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    return session


async def get_user_session_and_runner(
    user_id: str,
    agent,
    session_id: Optional[str] = None,
    app_name: str = None
) -> tuple[Session, Runner]:
    """
    Get session and create runner for an agent
    
    Args:
        user_id: User identifier
        agent: ADK agent instance
        session_id: Optional existing session ID
        app_name: Application name
    
    Returns:
        Tuple of (Session, Runner)
    """
    session_service = get_session_service()
    app_name = app_name or Config.APP_NAME
    
    # Get or create session
    session = await get_user_session(user_id, session_id, app_name)
    
    # Create runner
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )
    
    return session, runner


async def run_agent_with_session(
    runner: Runner,
    session: Session,
    content: types.Content
) -> AsyncGenerator[Any, None]:
    """
    Run agent and yield events
    
    Args:
        runner: ADK Runner instance
        session: Session object
        content: User message content
    
    Yields:
        ADK events from agent execution
    """
    events = runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content
    )
    
    async for event in events:
        yield event


def process_agent_event(event) -> Optional[Dict[str, Any]]:
    """
    Process ADK event and convert to frontend-friendly format
    
    Args:
        event: ADK event object
    
    Returns:
        Dictionary with event data or None if event should be skipped
    """
    # Skip events without content
    if not event.content:
        return None
    
    # Handle final response
    if event.is_final_response():
        if event.content.parts:
            text = ''.join(part.text or '' for part in event.content.parts if part.text)
            if text:
                return {
                    "type": "agent_response",
                    "author": event.author,
                    "content": text,
                    "final": True
                }
    
    # Handle intermediate responses
    if event.content.parts:
        text = ''.join(part.text or '' for part in event.content.parts if part.text)
        if text:
            return {
                "type": "agent_response",
                "author": event.author,
                "content": text,
                "final": False
            }
    
    # Handle tool calls
    if event.content.parts:
        for part in event.content.parts:
            if part.function_call:
                return {
                    "type": "tool_call",
                    "tool": part.function_call.name,
                    "args": part.function_call.args
                }
            if part.function_response:
                return {
                    "type": "tool_response",
                    "tool": part.function_response.name,
                    "response": part.function_response.response
                }
    
    return None


async def list_user_sessions(
    user_id: str,
    app_name: str = None,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    List sessions for a user with pagination
    
    Args:
        user_id: User identifier
        app_name: Application name
        page: Page number (1-indexed)
        page_size: Number of sessions per page
    
    Returns:
        Dictionary with sessions list and pagination info
    """
    session_service = get_session_service()
    app_name = app_name or Config.APP_NAME
    
    # ADK doesn't have built-in pagination, so we fetch all and paginate manually
    # In production, you'd want to implement this at the database level
    try:
        # This is a simplified version - ADK's session service may have different methods
        # You might need to query the database directly for pagination
        sessions = []
        
        return {
            "sessions": sessions[
                (page - 1) * page_size : page * page_size
            ],
            "total": len(sessions),
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        return {
            "sessions": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "error": str(e)
        }
