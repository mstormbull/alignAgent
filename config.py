"""
Configuration module for Company Alignment Facilitator

This module contains all configuration settings, constants, and environment variables
used throughout the application.
"""

import os
from typing import Optional

class Config:
    """Application configuration class"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Interview Configuration
    MAX_INTERVIEW_TURNS: int = 5
    
    # File System Configuration
    CONVERSATIONS_DIR: str = "conversations"
    
    # Document Processing Configuration
    CHUNK_SIZE: int = 4000
    CHUNK_OVERLAP: int = 200
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return True
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories"""
        os.makedirs(cls.CONVERSATIONS_DIR, exist_ok=True) 