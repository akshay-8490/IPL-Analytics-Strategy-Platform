"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: match_info.py

Description:
    Orchestrates the complete ETL pipeline for IPL match
    information datasets.

Purpose:
    - Execute end-to-end ETL
    - Produce warehouse-ready match metadata
    - Serve as the public ETL interface

===========================================================
"""

from __future__ import annotations

import pandas as pd

from src.etl.cleaners import clean_dataframe
from src.etl.standardizers import standardize_dataframe
from src.etl.normalizers import normalize_dataframe
from src.etl.validators import validate_dataframe
from src.etl.feature_builder import build_features

def process_match_info(df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute the complete ETL pipeline for IPL match
    information.

    Parameters
    ----------
    df : pd.DataFrame
        Raw match information DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned, validated and feature-engineered
        match DataFrame.
    """

    df = clean_dataframe(df)

    df = standardize_dataframe(df)

    df = normalize_dataframe(df)

    df = validate_dataframe(df)

    df = build_features(df)

    return df

__all__ = [
    "process_match_info",
]