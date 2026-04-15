# toolbox/logging/app_logger.py

import os
import sys
from pathlib import Path

from loguru import logger

from toolbox.logging.request_context import get_request_id, get_user_id

# Pastikan folder logs tersedia
Path("logs").mkdir(exist_ok=True)

LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "DEBUG").upper()
APP_ENV = os.getenv("APP_ENV", "development").lower()
IS_PRODUCTION = APP_ENV == "production"

LOGGER_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "req=<magenta>{extra[request_id]}</magenta> | "
    "user=<yellow>{extra[user_id]}</yellow> | "
    "<cyan>{extra[logger_name]}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "{message}"
)

# Reset default handler bawaan loguru
logger.remove()

# Console logger
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format=LOGGER_FORMAT,
    colorize=True,
    backtrace=not IS_PRODUCTION,
    diagnose=not IS_PRODUCTION,  # matikan di production
    enqueue=True,
)

# File logger untuk error
logger.add(
    "logs/error.log",
    level="ERROR",
    format=LOGGER_FORMAT,
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    backtrace=not IS_PRODUCTION,
    diagnose=False,
    enqueue=True,
)

# File logger untuk semua aplikasi
logger.add(
    "logs/app.log",
    level=LOG_LEVEL,
    format=LOGGER_FORMAT,
    rotation="10 MB",
    retention="14 days",
    compression="zip",
    backtrace=not IS_PRODUCTION,
    diagnose=False,
    enqueue=True,
)


def get_logger(name: str | None = None):
    """
    Ambil logger yang sudah terikat dengan:
    - logger_name
    - request_id
    - user_id
    """
    return logger.bind(
        logger_name=name or "app",
        request_id=get_request_id() or "-",
        user_id=get_user_id() or "-",
    )


def refresh_logger(name: str | None = None):
    """
    Ambil logger baru dengan request context terbaru.
    Berguna jika context di-set setelah logger awal dibuat.
    """
    return get_logger(name=name)