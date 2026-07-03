import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CogniWeave Knowledge Compiler"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgrespassword@localhost:5432/cogniweave"
    REDIS_URL: str = "redis://localhost:6379"
    GEMINI_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/callback"
    DRIVE_ROOT_FOLDER: str = "CogniWeave"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
