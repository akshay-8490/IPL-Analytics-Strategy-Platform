from __future__ import annotations

import logging
import time
from typing import Any

from src.analytics.head_to_head import analyze_head_to_head
from src.analytics.match_analysis import analyze_matches
from src.analytics.player_analysis import analyze_players
from src.analytics.season_analysis import analyze_seasons
from src.analytics.summary import compute_executive_summary
from src.analytics.team_analysis import analyze_teams
from src.analytics.venue_analysis import analyze_venues

from src.data_access.analytics_loader import (
    load_analytics_datasets,
)
from src.models import AnalyticsDatasetBundle, AnalyticsPipelineResult

logger = logging.getLogger(__name__)

def _generate_executive_summary(
    datasets: AnalyticsDatasetBundle,
) -> dict[str, Any]:
    """
    Generate executive summary metrics.
    """

    logger.info("Generating executive summary.")

    return compute_executive_summary(
        datasets.match_df,
    )

def _run_business_analytics(
    datasets: AnalyticsDatasetBundle,
) -> dict[str, Any]:
    """
    Execute all business analytics modules.
    """

    logger.info("Running analytics.")

    return {
        "season": analyze_seasons(
            datasets.match_df,
        ),

        "team": analyze_teams(
            datasets.match_df,
        ),

        "venue": analyze_venues(
            datasets.match_df,
        ),

        "player": analyze_players(
            datasets.match_df,
        ),

        "match": analyze_matches(
            datasets.match_df,
        ),

        "head_to_head": analyze_head_to_head(
            datasets.match_df,
        ),
    }

def run_analytics_pipeline() -> AnalyticsPipelineResult:
    """
    Execute the complete analytics pipeline.

    The pipeline performs the following steps:

    1. Load analytical datasets from the warehouse.
    2. Generate executive summary metrics.
    3. Execute all business analytics modules.
    4. Return pipeline results.

    Returns
    -------
    AnalyticsPipelineResult
        Complete analytics pipeline results.
    """

    logger.info("Starting analytics pipeline.")

    start_time = time.perf_counter()
    status = "FAILURE"

    try:
        datasets = load_analytics_datasets()

        executive_summary = _generate_executive_summary(
            datasets,
        )

        analytics_results = _run_business_analytics(
            datasets,
        )

        status = "SUCCESS"
    except Exception:
        logger.exception("Analytics pipeline failed.")
        raise
    finally:
        execution_time = time.perf_counter() - start_time
        logger.info(
            "Pipeline completed in %.2f seconds.",
            execution_time,
        )

    return AnalyticsPipelineResult(
        dataset_bundle=datasets,
        executive_summary=executive_summary,
        analytics_results=analytics_results,
        execution_time=execution_time,
        status=status,
    )

__all__ = [
    "AnalyticsPipelineResult",
    "run_analytics_pipeline",
]