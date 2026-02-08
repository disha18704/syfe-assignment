"""
Logging setup shared across all components.
Provides a factory function to create named loggers with consistent formatting.
"""

import logging
import sys

from config import LOG_LEVEL

_configured = False

_RESET = "\033[0m"
_DIM = "\033[2m"
_BOLD = "\033[1m"
_LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",    # Cyan
    logging.INFO: "\033[32m",     # Green
    logging.WARNING: "\033[33m",  # Yellow
    logging.ERROR: "\033[31m",    # Red
    logging.CRITICAL: "\033[1;31m",  # Bold red
}


class ColoredConsoleFormatter(logging.Formatter):
    """Formatter that adds colors to level names and uses padded columns for alignment."""

    BASE_FMT = "%(asctime)s  %(name)-14s  %(levelname)s  %(message)s"
    DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, use_color: bool = True, **kwargs) -> None:
        super().__init__(fmt=self.BASE_FMT, datefmt=self.DATE_FMT, **kwargs)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        original = record.levelname
        record.levelname = f"{original:<8}"
        if self.use_color and record.levelno in _LEVEL_COLORS:
            record.levelname = f"{_LEVEL_COLORS[record.levelno]}{record.levelname}{_RESET}"
        try:
            return super().format(record)
        finally:
            record.levelname = original


def _configure_root_logger() -> None:
    """Configure the root logger with console and file handlers."""
    global _configured
    if _configured:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    plain_fmt = "%(asctime)s  %(name)-14s  %(levelname)-8s  %(message)s"
    plain_formatter = logging.Formatter(fmt=plain_fmt, datefmt="%Y-%m-%d %H:%M:%S")

    use_color = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
    console_formatter = ColoredConsoleFormatter(use_color=use_color)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler("system.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(plain_formatter)
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
