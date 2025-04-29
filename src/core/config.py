from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
import os
from datetime import timedelta
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "kd-schedule"
    DEBUG: bool = False

    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000

    GRPC_SERVER_PORT: int = 50051

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    SQLALCHEMY_ECHO: bool = False

    LOG_SENSITIVE_DATA: list[str] = ["name"]
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = (
        "%(asctime)s | %(levelname)-8s | %(name)s | [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s"
    )
    LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    _LOGS_DIR: Path = BASE_DIR / "logs"

    @property
    def LOGS_DIR(self) -> Path:
        os.makedirs(self._LOGS_DIR, exist_ok=True)
        return self._LOGS_DIR

    # ---SERVICE SETTINGS---
    NEXT_TAKING_TIMING: timedelta = timedelta(hours=1)

    MORNING_HOUR: int = 8
    EVENING_HOUR: int = 22


settings = Settings()
