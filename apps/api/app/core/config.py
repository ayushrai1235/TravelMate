from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Dynamically locate the root .env file by walking up the directory tree
_current_file = Path(__file__).resolve()
_root_env = None
for _p in [_current_file] + list(_current_file.parents):
    if (_p / ".env").exists() and (_p / "apps").exists():
        _root_env = _p / ".env"
        break
_env_file_path = _root_env if _root_env else Path(".env")




class Settings(BaseSettings):
    PROJECT_NAME: str = "TravelMate AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"

    # Supabase / Postgres Database Connection
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:54322/postgres"
    REDIS_URL: str = "redis://localhost:6379/0"

    # External integrations default to deterministic mocks in local development.
    MOCK_EXTERNAL_APIS: bool = True
    HTTP_TIMEOUT_SECONDS: float = 8.0

    GOOGLE_MAPS_API_KEY: str | None = None
    RAILRADAR_API_KEY: str | None = None
    OPENWEATHER_API_KEY: str | None = None
    OPENWEATHERMAP_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL_NAME: str = "gemini-3.5-flash"

    model_config = SettingsConfigDict(
        env_file=str(_env_file_path),
        env_ignore_empty=True,
        extra="ignore"
    )


settings = Settings()
