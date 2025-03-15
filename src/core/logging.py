import sys
import logging
from logging.handlers import RotatingFileHandler

from src.core.config import settings


def get_formatter() -> logging.Formatter:
    return logging.Formatter(
        settings.LOG_FORMAT,
        datefmt=settings.LOG_DATE_FORMAT
    )


def get_logger(name: str, level: int | None = None) -> logging.Logger:
    if level is None:
        level = getattr(logging, settings.LOG_LEVEL)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(get_formatter())
        logger.addHandler(console_handler)
        
        logs_dir = settings.LOGS_DIR
        file_handler = RotatingFileHandler(
            logs_dir / f"{settings.APP_NAME}.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(get_formatter())
        logger.addHandler(file_handler)
        
        error_file_handler = RotatingFileHandler(
            logs_dir / f"{settings.APP_NAME}_error.log",
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(get_formatter())
        logger.addHandler(error_file_handler)
    
    return logger


def setup_app_logging() -> None:
    logging.getLogger("uvicorn.access").disabled = True
