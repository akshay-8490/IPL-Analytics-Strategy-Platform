"""
Match-level analytical summaries for IPL matches.

This module provides reusable match-wise analytics derived from the
processed match metadata dataset.

It computes match type distributions, result summaries, toss
behavior, and winning margin statistics without modifying the
input dataframe.
"""

from __future__ import annotations

import pandas as pd

from src.analytics.validators import (
    validate_required_columns,
)
from src.schemas.columns import (
    MATCH_TYPE_COL,
    TOSS_DECISION_COL,
    TOSS_WINNER_COL,
    WINNER_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

__all__ = [
    "analyze_matches",
]

REQUIRED_COLUMNS = {
    MATCH_TYPE_COL,
    WINNER_COL,
    TOSS_WINNER_COL,
    TOSS_DECISION_COL,
    WIN_BY_RUNS_COL,
    WIN_BY_WICKETS_COL,
}

def _match_type_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize IPL match types.
    """
    summary = (
        df[MATCH_TYPE_COL]
        .value_counts(dropna=False)
        .rename_axis("match_type")
        .reset_index(name="matches")
    )

    summary["percentage"] = (
        summary["matches"]
        / summary["matches"].sum()
        * 100
    ).round(2)

    return summary

def _result_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize IPL match results.
    """
    return pd.DataFrame({
        "metric": [
            "wins_by_runs",
            "wins_by_wickets",
            "no_results",
        ],
        "value": [
            (df[WIN_BY_RUNS_COL] > 0).sum(),
            (df[WIN_BY_WICKETS_COL] > 0).sum(),
            df[WINNER_COL].isna().sum(),
        ],
    })

def _toss_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarize toss decisions.
    """
    return (
        df[TOSS_DECISION_COL]
        .value_counts()
        .rename_axis("toss_decision")
        .reset_index(name="matches")
    )

def _toss_advantage_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Analyze the relationship between winning the toss and
    winning the match.

    Parameters
    ----------
    df : pd.DataFrame
        Match-level dataframe.

    Returns
    -------
    pd.DataFrame
        Summary showing whether the toss winner also won
        the match.
    """
    toss_advantage = (
        df.assign(
            toss_advantage=(
                df[TOSS_WINNER_COL]
                == df[WINNER_COL]
            )
        )
        .groupby(
            "toss_advantage",
            observed=True,
        )
        .size()
        .reset_index(name="matches")
    )

    total_matches = toss_advantage["matches"].sum()

    toss_advantage["percentage"] = (
        toss_advantage["matches"]
        .div(total_matches)
        .mul(100)
        .round(2)
    )

    toss_advantage["toss_advantage"] = (
        toss_advantage["toss_advantage"]
        .map({
            True: "Won Toss & Match",
            False: "Won Toss Only",
        })
    )

    return toss_advantage

def _margin_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compute descriptive statistics for match winning margins.

    Parameters
    ----------
    df : pd.DataFrame
        Match-level dataframe.

    Returns
    -------
    pd.DataFrame
        Statistical summary of run and wicket margins.
    """
    summary = pd.DataFrame({
        "metric": [
            "mean",
            "median",
            "minimum",
            "maximum",
            "standard_deviation",
        ],
        "runs_margin": [
            df[WIN_BY_RUNS_COL].mean(),
            df[WIN_BY_RUNS_COL].median(),
            df[WIN_BY_RUNS_COL].min(),
            df[WIN_BY_RUNS_COL].max(),
            df[WIN_BY_RUNS_COL].std(),
        ],
        "wickets_margin": [
            df[WIN_BY_WICKETS_COL].mean(),
            df[WIN_BY_WICKETS_COL].median(),
            df[WIN_BY_WICKETS_COL].min(),
            df[WIN_BY_WICKETS_COL].max(),
            df[WIN_BY_WICKETS_COL].std(),
        ],
    })

    return summary.round(2)

def analyze_matches(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Generate match-level analytical summaries.
    """
    logger.info("Starting match analysis...")

    validate_required_columns(
        df,
        REQUIRED_COLUMNS,
    )

    results = {
        "match_types": _match_type_summary(df),
        "results": _result_summary(df),
        "toss": _toss_summary(df),
        "toss_advantage": _toss_advantage_summary(df),
        "margins": _margin_summary(df),
    }

    logger.info("Match analysis completed.")

    return results