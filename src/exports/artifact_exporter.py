"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: exporter.py

Description:
    Export utilities for ETL artifacts.

Purpose:
    - Export discovery artifacts.
    - Standardize dataset exports.
    - Centralize export operations.

===========================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.utils.io_utils import write_csv
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def export_dataframe(
    dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Export a DataFrame as CSV.

    Parameters
    ----------
    dataframe : pd.DataFrame

    output_path : Path
    """

    write_csv(
        dataframe=dataframe,
        output_path=output_path,
        index=False,
    )


def export_discovery_artifacts(
    catalog_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    report_df: pd.DataFrame,
    output_directory: Path,
) -> None:
    """
    Export all Notebook 01 artifacts.

    Parameters
    ----------
    catalog_df : pd.DataFrame

    metadata_df : pd.DataFrame

    report_df : pd.DataFrame

    output_directory : Path
    """

    logger.info("Exporting discovery artifacts...")

    export_dataframe(
        catalog_df,
        output_directory / "dataset_catalog.csv",
    )

    export_dataframe(
        metadata_df,
        output_directory / "dataset_metadata.csv",
    )

    export_dataframe(
        report_df,
        output_directory / "discovery_report.csv",
    )

    logger.info("Discovery artifacts exported successfully.")