import json
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any

from src.core.config import settings


class JSONFormatter(logging.Formatter):
    SENSITIVE_DATA = ["name"]

    def format(self, record: logging.LogRecord) -> str:

        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger_name": record.name,
            "filename": record.filename,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "context"):
            log_data["context"] = self.exclude_sensitive_data(record.context)

        return json.dumps(log_data)

    def exclude_sensitive_data(self, data: Any) -> Any:
        """Recursively mask sensitive data"""

        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == "body" and isinstance(value, str) and "{" in value:
                    try:
                        body_json = json.loads(value)
                        for json_key in body_json.keys():
                            if isinstance(body_json[json_key], dict):
                                self.exclude_sensitive_data(body_json[json_key])
                            if json_key in self.SENSITIVE_DATA:
                                body_json[json_key] = "SENSITIVE DATA"
                        result[key] = json.dumps(body_json)
                    except Exception:
                        result[key] = value
                elif key in self.SENSITIVE_DATA:
                    result[key] = "SENSITIVE DATA"
                elif isinstance(value, (dict, list)):
                    result[key] = self.exclude_sensitive_data(value)
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            return [self.exclude_sensitive_data(item) for item in data]
        else:
            return data


def get_json_formatter() -> JSONFormatter:
    return JSONFormatter(datefmt=settings.LOG_DATE_FORMAT)


def get_formatter() -> logging.Formatter:
    return logging.Formatter(settings.LOG_FORMAT, datefmt=settings.LOG_DATE_FORMAT)


def get_logger(name: str, level: int | None = None) -> logging.Logger:
    if level is None:
        level = getattr(logging, settings.LOG_LEVEL)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(get_json_formatter())
        logger.addHandler(console_handler)

        logs_dir = settings.LOGS_DIR
        file_handler = RotatingFileHandler(
            logs_dir / f"{settings.APP_NAME}.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(get_json_formatter())
        logger.addHandler(file_handler)

    return logger
