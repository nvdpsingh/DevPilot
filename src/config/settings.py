"""
Configuration settings for the multi-agent system.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings."""
    
    # AI Configuration
    groq_api_key: str = Field(default="", description="Groq API key")
    ai_model: str = Field(default="llama-3.1-8b-instant", description="AI model to use")
    
    # TestSprite Configuration
    testsprite_api_key: str = Field(default="", description="TestSprite API key")
    testsprite_mcp_url: str = Field(default="http://localhost:3000", description="TestSprite MCP URL")
    
    # Project Configuration
    projects_dir: str = Field(default="custom_projects", description="Directory for custom projects")
    plans_dir: str = Field(default="project_plans", description="Directory for project plans")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Global settings instance
settings = Settings()
