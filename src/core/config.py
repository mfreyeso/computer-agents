from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Computer Use Control Plane"
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://user:password@localhost:5432/computer_use"
    ANTHROPIC_API_KEY: str = ""
    # VNC
    VNC_HOST: str = "localhost" # Overridden in Docker Compose to "vnc_target"
    VNC_PORT: int = 5900

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

settings = Settings()
