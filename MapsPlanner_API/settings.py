import os
import enum
from pathlib import Path
from tempfile import gettempdir
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

from yarl import URL

TEMP_DIR = Path(gettempdir())

from os import environ


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = environ.get("api_host", "127.0.0.1")
    port: int = environ.get("api_port", 8000)
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    # Variables for the database
    db_host: str = environ.get("db_host", "localhost")
    db_port: int = environ.get("db_port", 5432)
    db_user: str = environ.get("db_user")
    db_pass: str = environ.get("db_pass")
    db_base: str = environ.get("db_base")
    db_echo: bool = environ.get("db_echo", True)

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MAPSPLANNER_API_",
        env_file_encoding="utf-8",
    )


settings = Settings()
