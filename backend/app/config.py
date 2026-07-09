# app/config.py
# Single source of truth for all configuration.
# Instead of os.environ.get() scattered everywhere,
# you import settings.OPENAI_API_KEY from one place.
# If any required variable is missing, app crashes on
# startup with a clear error — not 3 hours later.

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./preppath.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OPENAI_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = "preppath-dev"
    LANGCHAIN_API_KEY: str = ""
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()