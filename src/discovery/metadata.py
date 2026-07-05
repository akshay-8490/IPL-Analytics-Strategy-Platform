"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: metadata.py

Description:
    Build the IPL metadata DataFrame.

Purpose:
    - Parse every *_info.csv file.
    - Convert MatchMetadata objects into a DataFrame.
    - Return a consolidated metadata table.

===========================================================
"""

from __future__ import annotations

import pandas as pd

from pathlib import Path

from src.discovery.parser import MatchInfoParser
from src.utils.dataframe_utils import objects_to_dataframe
from src.models import MatchMetadata
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def build_dataset_metadata(
    catalog_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build dataset metadata.

    Parameters
    ----------
    catalog_df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """

    logger.info("Starting metadata extraction...")

    parser = MatchInfoParser()

    metadata_objects: list[MatchMetadata] = []

    for info_file in catalog_df["info_file"]:

        if pd.isna(info_file):
            continue

        metadata: MatchMetadata = parser.parse(
            Path(info_file)
        )

        metadata_objects.append(metadata)

        metadata_df = objects_to_dataframe(metadata_objects)

    metadata_df = (
        metadata_df
        .sort_values("match_id")
        .reset_index(drop=True)
    )

    logger.info(
        "Metadata extracted for %d matches.",
        len(metadata_df)
    )

    return metadata_df