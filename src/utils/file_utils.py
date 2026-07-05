"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: file_utils.py

Description:
    Utility functions for file and directory operations.

Purpose:
    - Validate project directories.
    - Discover Cricsheet CSV files.
    - Extract match IDs from filenames.
    - Classify CSV files.
    - Pair info and delivery files.

===========================================================
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


INFO_SUFFIX = "_info.csv"
CSV_EXTENSION = ".csv"


def validate_directory(directory: Path) -> None:
    """
    Validate that a directory exists.

    Parameters
    ----------
    directory : Path
        Directory to validate.

    Raises
    ------
    FileNotFoundError
        If the directory does not exist.
    """

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    if not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory.")


def ensure_directory_exists(directory: Path) -> None:
    """
    Create a directory if it does not already exist.

    Parameters
    ----------
    directory : Path
        Directory path.
    """

    directory.mkdir(parents=True, exist_ok=True)


def get_csv_files(directory: Path) -> List[Path]:
    """
    Return all CSV files from a directory.

    Parameters
    ----------
    directory : Path

    Returns
    -------
    List[Path]
        Sorted list of CSV files.
    """

    validate_directory(directory)

    files = list(directory.glob("*.csv"))
    if not files:
        files = list(directory.rglob("*.csv"))

    return sorted(files)


def extract_match_id(file_path: Path) -> int:
    """
    Extract the Cricsheet match ID from a filename.

    Examples
    --------
    335982.csv
    335982_info.csv

    Returns
    -------
    int
    """

    match = re.match(r"(\d+)", file_path.stem)

    if match is None:
        raise ValueError(
            f"Unable to extract match ID from '{file_path.name}'."
        )

    return int(match.group(1))


def classify_csv_file(file_path: Path) -> str:
    """
    Classify a Cricsheet CSV file.

    Returns
    -------
    str

    INFO
    or
    DELIVERY
    """

    if file_path.name.endswith(INFO_SUFFIX):
        return "INFO"

    return "DELIVERY"


def pair_match_files(csv_files: List[Path]) -> Dict[int, Dict]:
    """
    Pair delivery and info files by match ID.

    Parameters
    ----------
    csv_files : List[Path]

    Returns
    -------
    Dict

    {
        match_id:
        {
            info_file,
            delivery_file
        }
    }
    """

    catalog = {}

    for file in csv_files:

        try:
            match_id = extract_match_id(file)
        except ValueError as e:
            logger.warning("Skipping non-match CSV file: %s (%s)", file.name, e)
            continue

        if match_id not in catalog:

            catalog[match_id] = {
                "match_id": match_id,
                "info_file": None,
                "delivery_file": None,
            }

        file_type = classify_csv_file(file)

        if file_type == "INFO":

            catalog[match_id]["info_file"] = file

        else:

            catalog[match_id]["delivery_file"] = file

    return catalog


def list_files(directory: Path) -> List[str]:
    """
    Return filenames from a directory.

    Parameters
    ----------
    directory : Path

    Returns
    -------
    List[str]
    """

    validate_directory(directory)

    return sorted(file.name for file in directory.iterdir())