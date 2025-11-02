"""
Database configuration for ADK integration
Supports SQLite for development and PostgreSQL for production
"""

import os
from typing import Optional
from google.adk.sessions import DatabaseSessionService
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./v0clone.db")


def get_session_service() -> DatabaseSessionService:
    """
    Create and return ADK DatabaseSessionService
    
    Returns:
        DatabaseSessionService instance configured for the database
    """
    return DatabaseSessionService(db_url=DATABASE_URL)


async def init_database():
    """
    Initialize database tables for ADK session storage
    This is called on application startup
    """
    session_service = get_session_service()
    
    # ADK's DatabaseSessionService automatically creates required tables
    # on first use, but we can explicitly initialize if needed
    try:
        # Test connection by attempting to create a test session
        test_session = await session_service.create_session(
            app_name="test",
            user_id="test_user"
        )
        # Clean up test session
        if test_session:
            print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise
