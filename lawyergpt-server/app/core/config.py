from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./lawyergpt.db"
    openai_api_key: str = ""
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    frontend_origin: str = "http://localhost:3000"
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50


settings = Settings()
