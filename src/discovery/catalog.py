"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: catalog.py

Description:
    Build the master dataset catalog from Cricsheet files.

Purpose:
    - Discover all IPL match files.
    - Pair info and delivery files.
    - Build a catalog DataFrame.
    - Add validation flags.

===========================================================
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path

from src.utils.file_utils import (
    get_csv_files,
    pair_match_files,
)

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _convert_to_dataframe(catalog: dict) -> pd.DataFrame:
    """
    Convert catalog dictionary to DataFrame.
    """

    if not catalog:
        return pd.DataFrame(columns=["match_id", "info_file", "delivery_file"])

    return (
        pd.DataFrame(catalog.values())
        .sort_values("match_id")
        .reset_index(drop=True)
    )


def _add_validation_columns(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add dataset validation flags.
    """

    dataframe["has_info"] = (
        dataframe["info_file"].notna()
    )

    dataframe["has_delivery"] = (
        dataframe["delivery_file"].notna()
    )

    dataframe["is_complete"] = (
        dataframe["has_info"]
        &
        dataframe["has_delivery"]
    )

    return dataframe


def build_dataset_catalog(
    raw_data_directory: Path,
) -> pd.DataFrame:
    """
    Build the master dataset catalog.

    Parameters
    ----------
    raw_data_directory : Path

    Returns
    -------
    pd.DataFrame
    """

    logger.info("Starting dataset discovery...")

    csv_files = get_csv_files(raw_data_directory)

    logger.info(
        "CSV files discovered: %d",
        len(csv_files),
    )

    catalog = pair_match_files(csv_files)

    catalog_df = _convert_to_dataframe(catalog)

    catalog_df = _add_validation_columns(catalog_df)

    logger.info(
        "Matches discovered: %d",
        len(catalog_df),
    )

    logger.info("Dataset catalog successfully built.")

    return catalog_df
