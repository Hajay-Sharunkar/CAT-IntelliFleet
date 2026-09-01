from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "CAT IntelliFleet"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "sqlite:///./cat_intellifleet.db"

    secret_key: str = "CHANGE_ME_TO_A_RANDOM_SECRET"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    ai_provider: str = ""
    ai_api_key: str = ""


settings = Settings()
