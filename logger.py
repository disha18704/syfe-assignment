"""
Logging setup shared across all components.
Provides a factory function to create named loggers with consistent formatting.
"""

import logging
import sys

from config import LOG_LEVEL

# Flag to ensure we only configure the root logger once
_configured = False


def _configure_root_logger() -> None:
    """Configure the root logger with console and file handlers."""
    global _configured
    if _configured:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler — logs to stderr so it doesn't mix with CLI output
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler — persists logs for later review
    file_handler = logging.FileHandler("system.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # Always capture DEBUG to file
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    _configured = True


def get_logger(component_name: str) -> logging.Logger:
    """
    Get a named logger for a specific component.

    Args:
        component_name: Name of the component (e.g., "Manager", "MCP", "Specialist").

    Returns:
        A configured logging.Logger instance.
    """
    _configure_root_logger()
    return logging.getLogger(component_name)
