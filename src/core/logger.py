import logging
from logging.handlers import RotatingFileHandler
import json

from typing import Any

import structlog
from src.core.config import settings


def setup_logging(level: int | str) -> None:
    handlers = []

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    handlers.append(console_handler)

    file_handler = RotatingFileHandler(
        settings.LOGS_DIR / f"{settings.APP_NAME}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setLevel(level)
    handlers.append(file_handler)

    logging.basicConfig(
        format="%(message)s",
        handlers=handlers,
        level=level,
    )


def get_logger(name: str, level: int | str = settings.LOG_LEVEL) -> structlog.BoundLogger:
    setup_logging(level)
    render_method = (
        structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer()
    )
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt=settings.LOG_DATE_FORMAT, utc=True),
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            mask_sensitive_data,
            render_method,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger(name)


def mask_sensitive_data(logger, method_name, event_dict):
    """Recursively mask sensitive data"""

    def _mask_data(data: Any) -> Any:
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                    try:
                        result[key] = _mask_data(json.loads(value))
                    except:
                        result[key] = value
                elif key in settings.LOG_SENSITIVE_DATA:
                    result[key] = "SENSITIVE DATA"
                elif isinstance(value, (dict, list)):
                    result[key] = _mask_data(value)
                else:
                    result[key] = value
            return result
        elif isinstance(data, list):
            return [_mask_data(item) for item in data]
        else:
            return data

    if "context" in event_dict:
        event_dict["context"] = _mask_data(event_dict["context"])

    return event_dict
