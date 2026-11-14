from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="flexd-jobx-web", min_length=1)
    app_env: str = "development"
    app_cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    db_host: str = Field(default="127.0.0.1", min_length=1)
    db_port: int = Field(default=3306, ge=1, le=65535)
    db_name: str = Field(default="flexd_jobx", min_length=1)
    db_user: str = Field(default="flexd_jobx", min_length=1)
    db_password: SecretStr = SecretStr("")
    db_ssl_ca: Path | None = None
    db_ssl_disabled: bool = True

    storage_cloud_provider: str = "aws"
    storage_key: SecretStr = SecretStr("")
    storage_secret: SecretStr = SecretStr("")
    storage_region: str = "ap-southeast-1"
    storage_bucket: str = ""
    storage_path: str = "/jobx"
    storage_public_url: HttpUrl | None = None
    storage_acl: bool = False

    jwt_secret_key: SecretStr = SecretStr("")
    jwt_algorithm: Literal["HS256"] = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1)
    jwt_issuer: str = "jobx"
    jwt_audience: str = "jobx-api"

    llm_base_url: HttpUrl = HttpUrl("https://api.openai.com/v1")
    llm_api_key: SecretStr = SecretStr("")
    llm_model: str = ""
    llm_timeout_seconds: int = Field(default=60, ge=1)
    llm_max_retries: int = Field(default=2, ge=0, le=10)

    @property
    def database_url(self) -> URL:
        return URL.create(
            "mysql+pymysql",
            username=self.db_user,
            password=self.db_password.get_secret_value(),
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
