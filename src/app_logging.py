"""Structured logging helpers for SpecWise AI."""

import json
import logging
import sys
from contextlib import contextmanager
from time import perf_counter
from typing import Any, Iterator

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger instance."""
    logger = logging.getLogger(name)

    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format=_LOG_FORMAT,
            handlers=[logging.StreamHandler(sys.stdout)],
        )

    return logger


def log_event(logger: logging.Logger, event: str, level: int = logging.INFO, **details: Any) -> None:
    """Write a structured log event as JSON details."""
    payload = json.dumps(details, ensure_ascii=False, default=str)
    logger.log(level, "%s | %s", event, payload)


@contextmanager
def timed_event(logger: logging.Logger, event: str, **details: Any) -> Iterator[None]:
    """Log start/end duration for an operation."""
    start_time = perf_counter()
    log_event(logger, f"{event}_started", **details)

    try:
        yield
    except Exception as error:
        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        log_event(
            logger,
            f"{event}_failed",
            level=logging.ERROR,
            duration_ms=duration_ms,
            error_type=type(error).__name__,
            error_message=str(error),
            **details,
        )
        raise
    else:
        duration_ms = round((perf_counter() - start_time) * 1000, 2)
        log_event(logger, f"{event}_completed", duration_ms=duration_ms, **details)
