from __future__ import annotations

from typing import List

from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = Field("dev", env="APP_ENV")
    backend_host: str = Field("127.0.0.1", env="BACKEND_HOST")
    backend_port: int = Field(8000, env="BACKEND_PORT")
    secret_key: str = Field("please-change-this-secret", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(60, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    db_host: str = Field("127.0.0.1", env="DB_HOST")
    db_port: int = Field(3306, env="DB_PORT")
    db_name: str = Field("lab_gpu_monitor", env="DB_NAME")
    db_user: str = Field("root", env="DB_USER")
    db_password: str = Field("", env="DB_PASSWORD")

    cors_allow_origins: str | List[str] = Field(default_factory=lambda: ["*"], env="CORS_ALLOW_ORIGINS")

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_cors_allow_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def sqlalchemy_database_uri(self) -> str:
        password = self.db_password or ""
        return (
            f"mysql+pymysql://{self.db_user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


settings = Settings()
