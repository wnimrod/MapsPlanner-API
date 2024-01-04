import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic import Extra
from pydantic_settings import BaseSettings, SettingsConfigDict

from yarl import URL

from MapsPlanner_API import Environment

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

    host: str = environ.get("host", "127.0.0.1")
    port: int = environ.get("port", 8000)
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    log_level: LogLevel = LogLevel.DEBUG

    # Current environment
    environment: Environment = Environment(environ["environment"])

    # Variables for the database
    db_host: str = environ["db_host"]
    db_port: int = environ["db_port"]
    db_user: str = environ["db_user"]
    db_pass: str = environ["db_pass"]
    db_base: str = environ["db_base"]
    db_echo: bool = environ.get("db_echo", False)

    backend_url: str = environ["backend_url"]
    frontend_url: str = environ["frontend_url"]

    user_auto_approval: bool = environ["user_auto_approval"]

    # Google auth variables
    google_auth_client_id: str = environ["google_auth_client_id"]
    google_auth_client_secret: str = environ["google_auth_client_secret"]

    # ChatGPT
    chatgpt_api_key: str = environ["chatgpt_api_key"]

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


settings = Settings()
