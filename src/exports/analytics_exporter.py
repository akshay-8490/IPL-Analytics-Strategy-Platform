from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from config.config import ANALYTICS_DATA_DIR
from src.models import AnalyticsPipelineResult

logger = logging.getLogger(__name__)

ANALYTICS_ROOT = ANALYTICS_DATA_DIR

EXECUTIVE_DIR = ANALYTICS_ROOT / "executive"

SEASON_DIR = ANALYTICS_ROOT / "season"

TEAM_DIR = ANALYTICS_ROOT / "team"

VENUE_DIR = ANALYTICS_ROOT / "venue"

PLAYER_DIR = ANALYTICS_ROOT / "player"

MATCH_DIR = ANALYTICS_ROOT / "match"

HEAD_TO_HEAD_DIR = ANALYTICS_ROOT / "head_to_head"

DOMAIN_DIRECTORIES = {
    "season": SEASON_DIR,
    "team": TEAM_DIR,
    "venue": VENUE_DIR,
    "player": PLAYER_DIR,
    "match": MATCH_DIR,
    "head_to_head": HEAD_TO_HEAD_DIR,
}

def _export_dataframe(
    dataframe: pd.DataFrame,
    output_dir: Path,
    filename: str,
) -> None:
    """
    Export a DataFrame as both CSV and Parquet.

    Parameters
    ----------
    dataframe : pd.DataFrame
        DataFrame to export.

    output_dir : Path
        Destination directory.

    filename : str
        Base filename without extension.
    """

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = output_dir / f"{filename}.csv"
    parquet_path = output_dir / f"{filename}.parquet"

    dataframe.to_csv(
        csv_path,
        index=False,
    )

    dataframe.to_parquet(
        parquet_path,
        index=False,
    )

    logger.info(
        "Exported '%s' to %s",
        filename,
        output_dir,
    )

def _export_json(
    data: dict[str, Any],
    output_path: Path,
) -> None:
    """
    Export a dictionary as JSON.

    Parameters
    ----------
    data : dict
        Dictionary to export.

    output_path : Path
        Destination JSON file.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            default=str,
        )

    logger.info(
        "Exported executive summary to %s",
        output_path,
    )

def _export_domain(
    domain: str,
    results: dict[str, pd.DataFrame],
) -> None:
    """
    Export all analytical artifacts for a domain.

    Parameters
    ----------
    domain : str
        Analytics domain.

    results : dict[str, pd.DataFrame]
        Named analytical artifacts.
    """

    if domain not in DOMAIN_DIRECTORIES:
        raise ValueError(
            f"Unknown domain '{domain}'. "
            f"Must be one of: {list(DOMAIN_DIRECTORIES.keys())}"
        )

    logger.info(
        "Exporting '%s' analytics.",
        domain,
    )

    output_dir = DOMAIN_DIRECTORIES[domain]

    for artifact_name, dataframe in results.items():

        _export_dataframe(
            dataframe=dataframe,
            output_dir=output_dir,
            filename=artifact_name,
        )

    logger.info("%s exported.", domain.replace("_", " ").title())

def export_analytics_results(
    pipeline_results: AnalyticsPipelineResult,
) -> None:
    """
    Export analytics pipeline results to the Analytics Data Mart.

    Parameters
    ----------
    pipeline_results : AnalyticsPipelineResult
        Results produced by the analytics pipeline.
    """

    logger.info("Exporting analytics results.")

    try:
        # Export executive summary
        _export_json(
            data=pipeline_results.executive_summary,
            output_path=EXECUTIVE_DIR / "executive_summary.json",
        )

        # Export analytical artifacts
        for (
            domain,
            results,
        ) in pipeline_results.analytics_results.items():

            _export_domain(
                domain=domain,
                results=results,
            )

        logger.info(
            "Analytics results exported successfully."
        )
    except Exception:
        logger.exception("Failed to export analytics results.")
        raise