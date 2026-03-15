from pydantic.v1 import BaseSettings, Field


class AppSettings(BaseSettings):
    app_name: str = Field("Zambia Law", env="APP_NAME")
    environment: str = Field("dev", env="ENVIRONMENT")
    upload_dir: str = Field(..., env="UPLOAD_DIR")
    max_upload_size: int = Field(..., env="MAX_UPLOAD_SIZE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DatabaseSettings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class SessionSettings(BaseSettings):
    session_secret_key: str = Field(..., env="SESSION_SECRET_KEY")
    session_expiry_minutes: int = Field(60, env="SESSION_EXPIRY_MINUTES")
    cookie_name: str = Field(..., env="COOKIE_NAME")
    algorithm: str = Field(..., env="ALGORITHM")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class HashingSettings(BaseSettings):
    ip_hash_secret_key: str = Field(..., env="IP_HASH_SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class Settings(AppSettings, DatabaseSettings, SessionSettings, HashingSettings):
    """
    One settings object to import everywhere.
    """
    pass


settings = Settings()
