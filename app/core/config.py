"""
Configuration Management System

This module provides type-safe configuration management using Pydantic.
All environment variables are validated and have proper defaults.
"""

import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with type validation and environment variable loading.
    
    This class automatically loads values from:
    1. Environment variables
    2. .env file
    3. Default values defined here
    """
    
    # =============================================================================
    # Application Settings
    # =============================================================================
    APP_NAME: str = "InscribeVerse"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    LOG_LEVEL: str = Field(default="DEBUG", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    
    # =============================================================================
    # Security Settings
    # =============================================================================
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    @validator("SECRET_KEY")
    def secret_key_must_be_strong(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    # =============================================================================
    # Server Configuration
    # =============================================================================
    HOST: str = "0.0.0.0"
    PORT: int = Field(default=8000, ge=1, le=65535)
    RELOAD: bool = True
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # =============================================================================
    # Database Configuration
    # =============================================================================
    DATABASE_URL: str = "postgresql+asyncpg://inscribeverse:dev_password@localhost:5432/inscribeverse_dev"
    DATABASE_ECHO: bool = True
    
    # Connection Pool Settings
    DATABASE_POOL_SIZE: int = Field(default=20, ge=1, le=100)
    DATABASE_MAX_OVERFLOW: int = Field(default=30, ge=0, le=100)
    DATABASE_POOL_TIMEOUT: int = Field(default=30, ge=1, le=300)
    
    # Test Database
    TEST_DATABASE_URL: Optional[str] = None
    
    @validator("DATABASE_URL")
    def database_url_must_be_postgres(cls, v):
        if not v.startswith("postgresql"):
            raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        return v
    
    # =============================================================================
    # Redis Configuration
    # =============================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_EXPIRE: int = Field(default=3600, ge=60)  # 1 hour default
    REDIS_SESSION_EXPIRE: int = Field(default=86400, ge=300)  # 24 hours default
    
    # =============================================================================
    # AI/LangChain Configuration
    # =============================================================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=2.0)
    OPENAI_MAX_TOKENS: int = Field(default=2000, ge=1, le=8000)
    
    # LangChain Settings
    LANGCHAIN_CACHE_ENABLED: bool = True
    LANGCHAIN_VERBOSE: bool = False
    
    # =============================================================================
    # Email Configuration
    # =============================================================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = Field(default=587, ge=1, le=65535)
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = "noreply@inscribeverse.com"
    EMAILS_FROM_NAME: str = "InscribeVerse"
    
    # =============================================================================
    # File Storage Configuration
    # =============================================================================
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = Field(default=10485760, ge=1024)  # 10MB default
    
    # AWS S3 (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = None
    
    # =============================================================================
    # Background Tasks (Celery)
    # =============================================================================
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    
    # =============================================================================
    # Rate Limiting
    # =============================================================================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1)
    RATE_LIMIT_WINDOW: int = Field(default=60, ge=1)  # seconds
    
    # =============================================================================
    # Monitoring and Logging
    # =============================================================================
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = Field(default=9090, ge=1, le=65535)
    
    # Sentry Error Tracking
    SENTRY_DSN: Optional[str] = None
    
    # Structured Logging
    LOG_FORMAT: str = Field(default="json", pattern="^(json|text)$")
    LOG_FILE: str = "./logs/app.log"
    
    # =============================================================================
    # Feature Flags
    # =============================================================================
    ENABLE_ADMIN_ROUTES: bool = True
    ENABLE_AI_FEATURES: bool = True
    ENABLE_BACKGROUND_TASKS: bool = True
    ENABLE_FILE_UPLOADS: bool = True
    
    # =============================================================================
    # API Documentation
    # =============================================================================
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    OPENAPI_URL: str = "/openapi.json"
    
    # =============================================================================
    # Development Settings
    # =============================================================================
    DEV_RESET_DB: bool = False
    DEV_LOAD_SAMPLE_DATA: bool = True
    
    # =============================================================================
    # Computed Properties
    # =============================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.ENVIRONMENT == "testing"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (for Alembic migrations)."""
        return self.DATABASE_URL.replace("+asyncpg", "")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS
    
    # =============================================================================
    # Validation Methods
    # =============================================================================
    @validator("ENVIRONMENT")
    def set_production_defaults(cls, v, values):
        """Set secure defaults for production environment."""
        if v == "production":
            # Override insecure defaults for production
            values.update({
                "DEBUG": False,
                "DATABASE_ECHO": False,
                "RELOAD": False,
                "LOG_LEVEL": "WARNING"
            })
        return v
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DATABASE_ECHO,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "pool_timeout": self.DATABASE_POOL_TIMEOUT,
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration dictionary."""
        return {
            "url": self.REDIS_URL,
            "cache_expire": self.REDIS_CACHE_EXPIRE,
            "session_expire": self.REDIS_SESSION_EXPIRE,
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration dictionary."""
        return {
            "allow_origins": self.cors_origins_list,
            "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
            "allow_methods": self.CORS_ALLOW_METHODS,
            "allow_headers": self.CORS_ALLOW_HEADERS,
        }
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True


# =============================================================================
# Global Settings Instance
# =============================================================================
settings = Settings()


# =============================================================================
# Environment-specific Settings
# =============================================================================
def get_settings() -> Settings:
    """
    Get settings instance. 
    This function can be used for dependency injection in FastAPI.
    """
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment (useful for testing)."""
    global settings
    settings = Settings()
    return settings 