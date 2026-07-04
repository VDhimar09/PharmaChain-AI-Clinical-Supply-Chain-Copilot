"""Shared logging configuration for PharmaChain AI components."""

from __future__ import annotations

import logging


LOGGER_NAME = "PharmaChainAI"


def _configure_root_logger() -> logging.Logger:
    """Configure and return the root application logger."""

    logger = logging.getLogger(LOGGER_NAME)

    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Return a consistently configured logger for a PharmaChain AI module.

    Args:
        name: Module or component name requesting a logger.

    Returns:
        A configured logger under the ``PharmaChainAI`` namespace.
    """

    root_logger = _configure_root_logger()
    child_name = f"{LOGGER_NAME}.{name}" if name else LOGGER_NAME
    child_logger = logging.getLogger(child_name)
    child_logger.setLevel(root_logger.level)
    return child_logger
