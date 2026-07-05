"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: logging_utils.py

Description:
    Centralized logging configuration for the project.

Purpose:
    - Configure consistent logging.
    - Provide reusable loggers.
    - Standardize log formatting across modules.

===========================================================
"""

from __future__ import annotations

import logging


LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logger(level: int = logging.INFO) -> None:
    """
    Configure the root logger for the project.

    Parameters
    ----------
    level : int, default=logging.INFO
        Logging level.
    """

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.

    Parameters
    ----------
    name : str
        Usually __name__.

    Returns
    -------
    logging.Logger
    """

    return logging.getLogger(name)