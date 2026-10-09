from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str = "change-me"
    cors_origins: str = "http://localhost:5173"
    database_url: str = "postgresql+asyncpg://scanner:scanner@db:5432/scanner"

    github_app_id: str = ""
    github_app_private_key: str = ""
    github_webhook_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""

    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5-5"


settings = Settings()
