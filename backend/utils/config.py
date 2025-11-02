"""
Configuration management utilities
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./v0clone.db")
    
    # App Settings
    APP_NAME = os.getenv("APP_NAME", "v0-clone")
    DEFAULT_SESSION_TTL = int(os.getenv("DEFAULT_SESSION_TTL", "3600"))
    
    # Model Configuration
    GEMINI_MODEL = "gemini-2.5-flash"
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        errors = []
        
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY not set")
        
        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY not set")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"⚠️  Configuration warning: {e}")
    print("   Please set the required environment variables in backend/.env")
