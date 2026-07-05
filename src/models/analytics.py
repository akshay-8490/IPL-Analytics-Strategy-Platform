from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import pandas as pd

@dataclass(frozen=True)
class AnalyticsDatasetBundle:
    """
    Canonical analytical datasets reconstructed from the warehouse.

    Attributes
    ----------
    match_df : pd.DataFrame
        Match-level analytical dataset.

    player_df : pd.DataFrame
        Player-match analytical dataset.

    delivery_df : pd.DataFrame
        Delivery-level analytical dataset.

    team_df : pd.DataFrame
        Team-normalized analytical dataset.

    head_to_head_df : pd.DataFrame
        Canonical team-pair analytical dataset.
    """

    match_df: pd.DataFrame

    player_df: pd.DataFrame

    delivery_df: pd.DataFrame

    team_df: pd.DataFrame

    head_to_head_df: pd.DataFrame


@dataclass(frozen=True)
class AnalyticsPipelineResult:
    """
    Results produced by the analytics pipeline.

    Attributes
    ----------
    dataset_bundle : AnalyticsDatasetBundle
        Canonical analytical datasets (infrastructure output). Downstream
        notebooks should consume executive_summary and analytics_results instead.

    executive_summary : dict[str, Any]
        Executive KPIs generated from the match dataset.

    analytics_results : dict[str, Any]
        Outputs from all business analytics modules.

    execution_time : float
        Pipeline execution time in seconds.

    status : str
        Pipeline execution status.
    """

    dataset_bundle: AnalyticsDatasetBundle

    executive_summary: dict[str, Any]

    analytics_results: dict[str, Any]

    execution_time: float

    status: str
