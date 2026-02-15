from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent
ENV_FILE = BASE_DIR / ".env"

class PostgresSettings(BaseModel):
    user: str
    password: str
    db: str
    host: str
    port: int
    url: PostgresDsn

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="_",
        extra="ignore"
    )
    postgres: PostgresSettings

settings = Settings()
