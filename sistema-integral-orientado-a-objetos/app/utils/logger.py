"""
Centralized logging configuration for Software FJ.

All important events and every exception are written to a log file
so the application remains auditable and never loses error context.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Log directory lives next to the project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_LOG_DIR = _PROJECT_ROOT / "logs"
_LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = _LOG_DIR / "software_fj.log"

_logger: logging.Logger | None = None


def setup_logger(name: str = "SoftwareFJ") -> logging.Logger:
    """Create and configure the application logger (singleton)."""
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Persistent file handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler (warnings and above only)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _logger = logger
    return logger


def log_event(message: str) -> None:
    """Record an informational event."""
    setup_logger().info(message)


def log_exception(exc: BaseException, context: str = "") -> None:
    """
    Record an exception with full traceback.
    Supports exception chaining via exc.__cause__.
    """
    parts = [context, f"{type(exc).__name__}: {exc}"]
    if exc.__cause__:
        parts.append(
            f"Caused by: {type(exc.__cause__).__name__}: {exc.__cause__}"
        )
    setup_logger().error(" | ".join(filter(None, parts)), exc_info=True)
