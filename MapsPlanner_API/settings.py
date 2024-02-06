import enum
from pathlib import Path
from tempfile import gettempdir
from typing import Any, List

from pydantic import Extra
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

from MapsPlanner_API import Environment
from MapsPlanner_API.utils import JSONEncoder

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


class Settings(BaseSettings, extra=Extra.allow):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = environ["host"]
    port: int = environ["port"]
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    log_level: LogLevel = environ.get("log_level", LogLevel.DEBUG)

    # Current environment
    environment: Environment = Environment(environ["environment"])

    # Variables for the database
    db_host: str = environ["db_host"]
    db_port: int = environ["db_port"]
    db_user: str = environ["db_user"]
    db_pass: str = environ["db_pass"]
    db_base: str = environ["db_base"]
    db_echo: bool = log_level == LogLevel.DEBUG

    backend_url: str = environ["backend_url"]
    frontend_url: str = environ["frontend_url"]

    user_auto_approval: bool = environ["user_auto_approval"]

    # Google auth variables
    google_auth_client_id: str = environ["google_auth_client_id"]
    google_auth_client_secret: str = environ["google_auth_client_secret"]

    # ChatGPT
    chatgpt_api_key: str = environ.get("chatgpt_api_key")

    # Maptiler
    maptiler_api_key: str = environ.get("maptiler_api_key")

    # Allowed origins on cors

    @property
    def extra_allowed_origins(self) -> List[str]:
        allowed_origins = environ.get("allowed_origins") or []

        return [
            stripped_origin
            for allowed_origin in allowed_origins
            if len(stripped_origin := allowed_origin.strip()) > 0
        ]

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
        env_file_encoding="utf-8",
    )

    json_serializer: Any = JSONEncoder().encode


settings = Settings()
