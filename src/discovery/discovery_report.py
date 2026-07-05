"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: discovery_report.py

Description:
    Generate dataset discovery reports.

Purpose:
    - Convert validation results into a tabular report.
    - Provide an executive summary of dataset quality.

===========================================================
"""

from __future__ import annotations

import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def build_discovery_report(
    validation_report: dict,
) -> pd.DataFrame:
    """
    Build the dataset discovery report.

    Parameters
    ----------
    validation_report : dict

    Returns
    -------
    pd.DataFrame
    """

    logger.info("Building discovery report...")

    report_df = (
        pd.DataFrame(
            validation_report.items(),
            columns=[
                "Metric",
                "Value"
            ]
        )
        .reset_index(drop=True)
    )

    logger.info("Discovery report created.")

    return report_df