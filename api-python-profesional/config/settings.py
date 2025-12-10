"""
Configuration management for the Songs API.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    # Application settings
    APP_NAME: str = Field(default="Songs API", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Server settings
    HOST: str = Field(default="localhost", description="Server host")
    PORT: int = Field(default=5001, ge=1, le=65535, description="Server port")
    
    # Database settings
    DATABASE_PATH: str = Field(
        default="./data/db.json", 
        description="Path to JSON database file"
    )
    DATABASE_BACKUP_PATH: str = Field(
        default="./data/db_backup.json",
        description="Path to database backup file"
    )
    
    # API settings
    API_PREFIX: str = Field(default="/api/v1", description="API version prefix")
    ALLOWED_HOSTS: list[str] = Field(
        default=["localhost", "127.0.0.1"],
        description="Allowed hosts for CORS"
    )
    
    # Logging settings
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string"
    )
    
    # Validation settings
    MAX_SONGS_PER_REQUEST: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum songs allowed per request"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


# Environment-specific configurations
def get_environment_config() -> dict:
    """Get environment-specific configuration overrides."""
    env = os.getenv("ENVIRONMENT", "development")
    
    configs = {
        "development": {
            "DEBUG": True,
            "LOG_LEVEL": "DEBUG"
        },
        "production": {
            "DEBUG": False,
            "LOG_LEVEL": "WARNING"
        },
        "testing": {
            "DEBUG": True,
            "LOG_LEVEL": "DEBUG",
            "DATABASE_PATH": "./tests/fixtures/test_db.json"
        }
    }
    
    return configs.get(env, configs["development"])


# Apply environment-specific overrides
env_config = get_environment_config()
for key, value in env_config.items():
    if hasattr(settings, key):
        setattr(settings, key, value)