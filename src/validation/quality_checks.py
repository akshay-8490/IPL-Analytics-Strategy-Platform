"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: quality_checks.py

Description:
    Dataset validation utilities.

Purpose:
    - Validate dataset completeness.
    - Generate dataset quality statistics.
    - Produce a reusable validation report.

Author: Akshay Abhiraj
===========================================================
"""

from __future__ import annotations

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def validate_dataset(
    catalog_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
) -> dict:
    """
    Validate the discovered dataset.

    Parameters
    ----------
    catalog_df : pd.DataFrame

    metadata_df : pd.DataFrame

    Returns
    -------
    dict
        Validation report.
    """

    logger.info("Running dataset validation...")

    report = {

        # ---------- Catalog ----------

        "total_matches":
            len(catalog_df),

        "complete_matches":
            int(catalog_df["is_complete"].sum()),

        "missing_info_files":
            int((~catalog_df["has_info"]).sum()),

        "missing_delivery_files":
            int((~catalog_df["has_delivery"]).sum()),

        "duplicate_match_ids":
            int(catalog_df["match_id"].duplicated().sum()),

        # ---------- Metadata ----------

        "missing_season":
            int(metadata_df["season"].isna().sum()),

        "missing_date":
            int(metadata_df["date"].isna().sum()),

        "missing_team1":
            int(metadata_df["team1"].isna().sum()),

        "missing_team2":
            int(metadata_df["team2"].isna().sum()),

        "missing_venue":
            int(metadata_df["venue"].isna().sum()),

        "missing_city":
            int(metadata_df["city"].isna().sum()),

        "missing_winner":
            int(metadata_df["winner"].isna().sum()),

        # ---------- Statistics ----------

        "earliest_season":
            metadata_df["season"].min(),

        "latest_season":
            metadata_df["season"].max(),

        "unique_teams":

            len(
                set(
                    metadata_df["team1"].dropna()
                ).union(
                    metadata_df["team2"].dropna()
                )
            ),

        "unique_venues":
            metadata_df["venue"].nunique(),

        "unique_cities":
            metadata_df["city"].nunique(),

    }

    logger.info("Dataset validation completed.")

    return report