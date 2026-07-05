"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: io_utils.py

Description:
    Utility functions for reading and writing files.

Purpose:
    - Centralize file I/O operations.
    - Standardize CSV and JSON handling.
    - Automatically create output directories.
    - Provide consistent logging.

Author: Akshay Abhiraj
===========================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .file_utils import ensure_directory_exists
from .logging_utils import get_logger

logger = get_logger(__name__)


def read_csv(file_path: Path, **kwargs) -> pd.DataFrame:
    """
    Read a CSV file.

    Parameters
    ----------
    file_path : Path
        Path to CSV file.

    **kwargs
        Additional keyword arguments passed to pandas.read_csv().

    Returns
    -------
    pd.DataFrame
    """

    logger.info("Reading CSV: %s", file_path.name)

    return pd.read_csv(file_path, **kwargs)


def write_csv(
    dataframe: pd.DataFrame,
    output_path: Path,
    index: bool = False,
    **kwargs
) -> None:
    """
    Save a DataFrame as CSV.

    Parameters
    ----------
    dataframe : pd.DataFrame

    output_path : Path

    index : bool
        Whether to save DataFrame index.
    """

    ensure_directory_exists(output_path.parent)

    try:
        dataframe.to_csv(
            output_path,
            index=index,
            **kwargs
        )
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied: Unable to write to '{output_path}'. "
            f"Please check if the file is open in another application (such as Excel or Power BI) and close it, then try again."
        ) from e

    logger.info("CSV saved: %s", output_path)


def read_json(file_path: Path) -> Any:
    """
    Read a JSON file.

    Parameters
    ----------
    file_path : Path

    Returns
    -------
    Any
    """

    logger.info("Reading JSON: %s", file_path.name)

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(data: Any, output_path: Path, indent: int = 4) -> None:
    """
    Save data as JSON.

    Parameters
    ----------
    data : Any

    output_path : Path
    """

    ensure_directory_exists(output_path.parent)

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=indent
        )

    logger.info("JSON saved: %s", output_path)


def export_dataframe(
    dataframe: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Export a DataFrame.

    Wrapper around write_csv().

    Parameters
    ----------
    dataframe : pd.DataFrame

    output_path : Path
    """

    write_csv(
        dataframe=dataframe,
        output_path=output_path,
        index=False
    )

