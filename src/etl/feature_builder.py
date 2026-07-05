"""
===========================================================
IPL Analytics & Strategy Platform
-----------------------------------------------------------
File: feature_builder.py

Description:
    Builds analytics-ready features from normalized IPL
    match information.

Purpose:
    - Build margin features
    - Build match features
    - Build calendar features
    - Build target features
    - Provide reusable feature engineering pipeline

Author: Akshay Abhiraj
===========================================================
"""

from __future__ import annotations

import pandas as pd

def build_margin_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build winning margin features.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with winning margin features.
    """
    df = df.copy()

    if {
        "winner_runs",
        "winner_wickets",
    }.issubset(df.columns):

        df["win_type"] = pd.NA

        df.loc[
            df["winner_runs"].notna(),
            "win_type",
        ] = "Runs"

        df.loc[
            df["winner_wickets"].notna(),
            "win_type",
        ] = "Wickets"

        df["winning_margin"] = (
            df["winner_runs"]
            .fillna(df["winner_wickets"])
            .astype("Int64")
        )

    return df

def build_match_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build match-level business features.
    """
    df = df.copy()

    if "winner" in df.columns:
        df["match_completed"] = df["winner"].notna()

    if {
        "team1",
        "team2",
    }.issubset(df.columns):

        df["match_fixture"] = (
            df["team1"]
            + " vs "
            + df["team2"]
        )

    return df

def build_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build calendar-based business features.
    """
    df = df.copy()

    if "match_month" in df.columns:

        df["season_phase"] = pd.cut(
            df["match_month"],
            bins=[0, 4, 5, 12],
            labels=[
                "Early",
                "Peak",
                "Late",
            ],
        )

    return df

def build_target_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build target variables for downstream analytics.
    """
    df = df.copy()

    if "winner" in df.columns:
        df["has_result"] = df["winner"].notna()

    return df

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering steps.
    """
    df = build_margin_features(df)
    df = build_match_features(df)
    df = build_calendar_features(df)
    df = build_target_features(df)

    return df

def compute_historical_batsman_stats(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cumulative historical career batsman stats prior to each match.
    """
    import numpy as np
    df = deliveries_df.copy()
    df["is_ball_faced"] = ~(df["wides"].fillna(0) > 0)
    df["is_striker_dismissed"] = (
        df["player_dismissed"].notna()
    ) & (df["player_dismissed"] == df["striker"])

    # Aggregation per match
    match_stats = (
        df.groupby(["match_id", "start_date", "striker"])
        .agg(
            match_runs=("runs_off_bat", "sum"),
            match_balls=("is_ball_faced", "sum"),
            match_dismissals=("is_striker_dismissed", "sum"),
        )
        .reset_index()
        .sort_values("start_date")
    )

    # Cumulative sums
    match_stats["cum_runs"] = match_stats.groupby("striker")["match_runs"].cumsum()
    match_stats["cum_balls"] = match_stats.groupby("striker")["match_balls"].cumsum()
    match_stats["cum_dismissals"] = match_stats.groupby("striker")["match_dismissals"].cumsum()

    # Prev stats (shift by 1 to represent stats PRIOR to the current match)
    match_stats["prev_runs"] = match_stats.groupby("striker")["cum_runs"].shift(1).fillna(0)
    match_stats["prev_balls"] = match_stats.groupby("striker")["cum_balls"].shift(1).fillna(0)
    match_stats["prev_dismissals"] = match_stats.groupby("striker")["cum_dismissals"].shift(1).fillna(0)

    # Calculate SR and Avg
    match_stats["batsman_career_runs"] = match_stats["prev_runs"].astype("Int64")
    match_stats["batsman_career_balls"] = match_stats["prev_balls"].astype("Int64")
    match_stats["batsman_career_sr"] = (
        (match_stats["prev_runs"] / match_stats["prev_balls"].replace(0, np.nan)) * 100
    ).fillna(0.0).round(2)

    # Average: runs / dismissals. If dismissals == 0, average is equal to total runs.
    match_stats["batsman_career_avg"] = (
        match_stats["prev_runs"] / match_stats["prev_dismissals"].replace(0, np.nan)
    ).fillna(match_stats["prev_runs"]).round(2)

    # Drop unnecessary columns
    cols_to_keep = [
        "match_id",
        "striker",
        "batsman_career_runs",
        "batsman_career_balls",
        "batsman_career_sr",
        "batsman_career_avg",
    ]
    return match_stats[cols_to_keep]

def compute_historical_bowler_stats(deliveries_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate cumulative historical career bowler stats prior to each match.
    """
    import numpy as np
    df = deliveries_df.copy()
    
    # Bowler wickets
    bowler_wicket_types = {
        "caught", "bowled", "lbw", "stumped", "caught and bowled", "hit wicket"
    }
    df["is_bowler_wicket"] = df["wicket_type"].isin(bowler_wicket_types)
    
    # Bowler runs (runs_off_bat + wides + noballs)
    df["bowler_runs"] = (
        df["runs_off_bat"]
        + df["wides"].fillna(0)
        + df["noballs"].fillna(0)
    )
    
    # Bowler balls bowled (excluding wides and noballs)
    df["is_ball_bowled"] = ~(df["wides"].fillna(0) > 0) & ~(df["noballs"].fillna(0) > 0)

    # Aggregation per match
    match_stats = (
        df.groupby(["match_id", "start_date", "bowler"])
        .agg(
            match_wickets=("is_bowler_wicket", "sum"),
            match_runs=("bowler_runs", "sum"),
            match_balls=("is_ball_bowled", "sum"),
        )
        .reset_index()
        .sort_values("start_date")
    )

    # Cumulative sums
    match_stats["cum_wickets"] = match_stats.groupby("bowler")["match_wickets"].cumsum()
    match_stats["cum_runs"] = match_stats.groupby("bowler")["match_runs"].cumsum()
    match_stats["cum_balls"] = match_stats.groupby("bowler")["match_balls"].cumsum()

    # Prev stats
    match_stats["prev_wickets"] = match_stats.groupby("bowler")["cum_wickets"].shift(1).fillna(0)
    match_stats["prev_runs"] = match_stats.groupby("bowler")["cum_runs"].shift(1).fillna(0)
    match_stats["prev_balls"] = match_stats.groupby("bowler")["cum_balls"].shift(1).fillna(0)

    # Calculate economy, wickets
    match_stats["bowler_career_wickets"] = match_stats["prev_wickets"].astype("Int64")
    match_stats["bowler_career_runs"] = match_stats["prev_runs"].astype("Int64")
    match_stats["bowler_career_balls"] = match_stats["prev_balls"].astype("Int64")
    
    # Economy: (runs / (balls / 6))
    match_stats["bowler_career_economy"] = (
        (match_stats["prev_runs"] / (match_stats["prev_balls"].replace(0, np.nan) / 6.0))
    ).fillna(0.0).round(2)

    # Drop unnecessary columns
    cols_to_keep = [
        "match_id",
        "bowler",
        "bowler_career_wickets",
        "bowler_career_runs",
        "bowler_career_balls",
        "bowler_career_economy",
    ]
    return match_stats[cols_to_keep]

__all__ = [
    "build_margin_features",
    "build_match_features",
    "build_calendar_features",
    "build_target_features",
    "build_features",
    "compute_historical_batsman_stats",
    "compute_historical_bowler_stats",
]