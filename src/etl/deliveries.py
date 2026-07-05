"""
Deliveries processing module.

This module parses Cricsheet ball-by-ball CSV files, standardizes team names,
performs basic cleaning, and consolidates deliveries across all matches.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
from tqdm import tqdm

from src.etl.standardizers import standardize_team_name
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "process_deliveries_dataset",
]

def process_deliveries_dataset(
    catalog_df: pd.DataFrame,
    raw_data_dir: Path,
) -> pd.DataFrame:
    """
    Compile, clean, and standardize ball-by-ball deliveries from raw CSVs.

    Parameters
    ----------
    catalog_df : pd.DataFrame
        Dataset catalog DataFrame mapping match IDs to raw files.
    raw_data_dir : Path
        Directory where raw CSV files are stored.

    Returns
    -------
    pd.DataFrame
        Consolidated and cleaned deliveries DataFrame.
    """
    logger.info("Starting processing of ball-by-ball deliveries...")

    # Filter catalog for complete matches that have delivery files
    valid_matches = catalog_df[
        catalog_df["is_complete"] & catalog_df["delivery_file"].notna()
    ]
    
    delivery_frames = []

    for _, row in tqdm(valid_matches.iterrows(), total=len(valid_matches), desc="Processing deliveries"):
        match_id = int(row["match_id"])
        file_name = f"{match_id}.csv"
        file_path = raw_data_dir / file_name

        if not file_path.exists():
            # Fallback recursive search if file is in a subdirectory
            matches = list(raw_data_dir.glob(f"**/{file_name}"))
            if matches:
                file_path = matches[0]
            else:
                logger.warning(f"Delivery file not found: {file_path}")
                continue

        try:
            # Read ball-by-ball CSV
            match_deliveries = pd.read_csv(file_path)
            delivery_frames.append(match_deliveries)
        except Exception as e:
            logger.error(f"Error reading delivery file for match {match_id}: {e}")
            continue

    if not delivery_frames:
        raise ValueError("No delivery files were successfully loaded.")

    # Combine all delivery DataFrames
    logger.info("Combining delivery files...")
    deliveries_df = pd.concat(delivery_frames, ignore_index=True)

    # Standardize and clean all text/categorical columns
    logger.info("Standardizing text/string columns...")
    text_cols = [
        "season",
        "venue",
        "batting_team",
        "bowling_team",
        "striker",
        "non_striker",
        "bowler",
        "wicket_type",
        "player_dismissed",
        "other_wicket_type",
        "other_player_dismissed",
        "fielder_1",
        "fielder_2",
        "fielder_3",
    ]
    for col in text_cols:
        if col in deliveries_df.columns:
            deliveries_df[col] = (
                deliveries_df[col]
                .astype(str)
                .replace({"nan": pd.NA, "None": pd.NA, "<NA>": pd.NA, "": pd.NA})
                .astype("string")
            )

    # Clean team names using canonical mapping
    logger.info("Standardizing team names in deliveries...")
    deliveries_df["batting_team"] = deliveries_df["batting_team"].apply(standardize_team_name).astype("string")
    deliveries_df["bowling_team"] = deliveries_df["bowling_team"].apply(standardize_team_name).astype("string")

    # Optimize data types to save memory
    logger.info("Optimizing data types...")
    int_cols = [
        "match_id",
        "innings",
        "actual_delivery",
        "runs_off_bat",
        "extras",
        "wides",
        "noballs",
        "byes",
        "legbyes",
        "penalty",
        "non_boundary",
    ]
    for col in int_cols:
        if col in deliveries_df.columns:
            deliveries_df[col] = pd.Series(
                pd.to_numeric(deliveries_df[col], errors="coerce"),
                index=deliveries_df.index,
                dtype="Int64"
            )

    logger.info(f"Processed deliveries compile completed! Total deliveries: {len(deliveries_df)}")
    return deliveries_df
