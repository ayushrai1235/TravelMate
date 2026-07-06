from pydantic_settings import BaseSettings, SettingsConfigDict


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
    RAILWAY_API_KEY: str | None = None
    RAILWAY_API_HOST: str = "railwayapi.p.rapidapi.com"
    OPENWEATHER_API_KEY: str | None = None
    OPENWEATHERMAP_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")


settings = Settings()
