"""Project-wide logging helpers that emit structured JSON.

Structured logs make it easier to inspect pipeline runs across the API and
Celery workers.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from .config import get_settings


class JsonFormatter(logging.Formatter):
    """Simple JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        base: Dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            base["stack"] = self.formatStack(record.stack_info)
        for key, value in getattr(record, "__dict__", {}).items():
            if key.startswith("_") or key in base:
                continue
            try:
                json.dumps(value)
                base[key] = value
            except TypeError:
                base[key] = str(value)
        return json.dumps(base)


def configure_logging() -> None:
    settings = get_settings()
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root_logger.addHandler(handler)
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    root_logger.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
