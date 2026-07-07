"""
export_validation_pipeline.py

This module orchestrates the project release pipeline. It executes validation,
packages all project outputs into a release directory structure, compiles project
statistics, and returns a pipeline result.
"""

from __future__ import annotations

import logging
import shutil
import time
from pathlib import Path
from typing import Any

import pandas as pd

from config.config import (
    ANALYTICS_DATA_DIR,
    DIMENSIONS_DIR,
    FACTS_DIR,
    MODELS_DIR,
    POWERBI_DATASET_DIR,
    RELEASE_DIR,
    STAGING_DIR,
)
from src.models.release import ReleasePipelineResult
from src.validation.project_validator import validate_project

logger = logging.getLogger(__name__)


def _copy_file_to_release(src_path: Path, relative_dir: Path) -> Path:
    """
    Copy a file to the release directory, creating directories as needed.
    """
    dest_dir = RELEASE_DIR / relative_dir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / src_path.name
    shutil.copy2(src_path, dest_path)
    return dest_path


def _package_release_artifacts() -> dict[str, int]:
    """
    Package all validated project artifacts to the release directory.
    """
    logger.info("Packaging project deliverables into the release folder.")
    counts = {
        "staging": 0,
        "warehouse": 0,
        "analytics": 0,
        "ml": 0,
        "powerbi": 0,
    }

    # 1. Package Processed Staging Data
    staging_files = [
        STAGING_DIR / "match_info_processed.parquet",
        STAGING_DIR / "deliveries_processed.parquet",
        STAGING_DIR / "match_features.parquet",
        STAGING_DIR / "player_features.parquet",
    ]
    for file_path in staging_files:
        if file_path.exists():
            _copy_file_to_release(file_path, Path("data/processed/staging"))
            counts["staging"] += 1

    # 2. Package Warehouse Conformed Files (Parquet & CSV)
    dimension_files = [
        DIMENSIONS_DIR / "dim_match.parquet",
        DIMENSIONS_DIR / "dim_team.parquet",
        DIMENSIONS_DIR / "dim_player.parquet",
        DIMENSIONS_DIR / "dim_venue.parquet",
        DIMENSIONS_DIR / "dim_season.parquet",
        DIMENSIONS_DIR / "dim_match.csv",
        DIMENSIONS_DIR / "dim_team.csv",
        DIMENSIONS_DIR / "dim_player.csv",
        DIMENSIONS_DIR / "dim_venue.csv",
        DIMENSIONS_DIR / "dim_season.csv",
    ]
    for file_path in dimension_files:
        if file_path.exists():
            _copy_file_to_release(file_path, Path("data/processed/warehouse/dimensions"))
            counts["warehouse"] += 1

    fact_files = [
        FACTS_DIR / "fact_match.parquet",
        FACTS_DIR / "fact_player_match.parquet",
        FACTS_DIR / "fact_delivery.parquet",
        FACTS_DIR / "fact_match.csv",
        FACTS_DIR / "fact_player_match.csv",
        FACTS_DIR / "fact_delivery.csv",
    ]
    for file_path in fact_files:
        if file_path.exists():
            _copy_file_to_release(file_path, Path("data/processed/warehouse/facts"))
            counts["warehouse"] += 1

    # 3. Package Analytics Mart
    # Copy executive summary and season summary
    exec_files = [
        ANALYTICS_DATA_DIR / "executive/executive_summary.json",
        ANALYTICS_DATA_DIR / "executive/season_summary.csv",
    ]
    for file_path in exec_files:
        if file_path.exists():
            _copy_file_to_release(file_path, Path("data/analytics/executive"))
            counts["analytics"] += 1

    # Copy domain folders
    domains = ["season", "team", "venue", "player", "match", "head_to_head"]
    for domain in domains:
        domain_dir = ANALYTICS_DATA_DIR / domain
        if domain_dir.exists():
            for file_path in domain_dir.iterdir():
                if file_path.is_file():
                    _copy_file_to_release(file_path, Path("data/analytics") / domain)
                    counts["analytics"] += 1

    # 4. Package ML Deliverables
    # Since MODELS_DIR is already in RELEASE_DIR/models, we do not copy them
    # to avoid SameFileError. We simply verify existence and increment count.
    ml_files = [
        MODELS_DIR / "benchmark_results.csv",
        MODELS_DIR / "classification_report.json",
        MODELS_DIR / "feature_importance.csv",
        MODELS_DIR / "confusion_matrix.csv",
    ]
    for file_path in ml_files:
        if file_path.exists():
            counts["ml"] += 1

    # 5. Build and package Power BI executive match dataset
    try:
        powerbi_df = _build_executive_match_dataset()
        powerbi_df.to_parquet(POWERBI_DATASET_DIR / "executive_match_dataset.parquet", index=False)
        powerbi_df.to_csv(POWERBI_DATASET_DIR / "executive_match_dataset.csv", index=False)
        counts["powerbi"] += 2
        logger.info("Power BI executive match dataset exported in Parquet and CSV formats (%d rows).", len(powerbi_df))
    except Exception:
        logger.exception("Failed to build Power BI executive match dataset.")

    # 6. Build and package Power BI team intelligence dataset
    try:
        team_intel_df = _build_team_intelligence_dataset()
        team_intel_df.to_parquet(POWERBI_DATASET_DIR / "team_intelligence_dataset.parquet", index=False)
        team_intel_df.to_csv(POWERBI_DATASET_DIR / "team_intelligence_dataset.csv", index=False)
        counts["powerbi"] += 2
        logger.info("Power BI team intelligence dataset exported in Parquet and CSV formats (%d rows).", len(team_intel_df))
    except Exception:
        logger.exception("Failed to build Power BI team intelligence dataset.")

    return counts


def _build_executive_match_dataset() -> pd.DataFrame:
    """
    Build a single flat match-level dataset designed for Power BI consumption.

    Schema
    ------
    match_id, season, match_date, team1, team2, winner, win_type,
    win_margin, venue, city, toss_winner, toss_decision,
    player_of_match, match_type, team1_score, team2_score, is_completed
    """
    logger.info("Building executive match dataset for Power BI.")

    matches = pd.read_parquet(STAGING_DIR / "match_info_processed.parquet")
    deliveries = pd.read_parquet(STAGING_DIR / "deliveries_processed.parquet")

    # Compute total runs per innings per match
    deliveries["total_runs"] = deliveries["runs_off_bat"] + deliveries["extras"]
    innings_scores = (
        deliveries
        .groupby(["match_id", "innings"])["total_runs"]
        .sum()
        .reset_index()
    )

    # Pivot innings 1 & 2 into team1_score / team2_score
    innings_1 = innings_scores[innings_scores["innings"] == 1].rename(
        columns={"total_runs": "team1_score"}
    )[["match_id", "team1_score"]]
    innings_2 = innings_scores[innings_scores["innings"] == 2].rename(
        columns={"total_runs": "team2_score"}
    )[["match_id", "team2_score"]]

    # Build the executive dataset
    executive = matches[[
        "match_id",
        "season",
        "date",
        "team1",
        "team2",
        "winner",
        "win_type",
        "winning_margin",
        "venue",
        "city",
        "toss_winner",
        "toss_decision",
        "player_of_match",
        "match_type",
    ]].copy()

    executive = executive.rename(columns={
        "date": "match_date",
        "winning_margin": "win_margin",
    })

    # Detect super overs (Ties)
    super_over_matches = set(deliveries[deliveries["innings"] > 2]["match_id"].unique())

    # Map win_type to explicit values: Runs, Wickets, Tie, No Result
    def map_win_type(row):
        wt = row["win_type"]
        if wt == "Runs":
            return "Runs"
        if wt == "Wickets":
            return "Wickets"
        if row["match_id"] in super_over_matches:
            return "Tie"
        return "No Result"

    executive["win_type"] = executive.apply(map_win_type, axis=1)

    # Add is_completed boolean column
    executive["is_completed"] = executive["win_type"].isin(["Runs", "Wickets", "Tie"])

    executive = executive.merge(innings_1, on="match_id", how="left")
    executive = executive.merge(innings_2, on="match_id", how="left")

    # Cast score columns to nullable integer
    executive["team1_score"] = executive["team1_score"].astype("Int64")
    executive["team2_score"] = executive["team2_score"].astype("Int64")

    return executive


def _build_team_intelligence_dataset() -> pd.DataFrame:
    """
    Build a single flat team-by-season dataset designed for Power BI consumption.

    Dataset Grain
    -------------
    One row = One Team x One IPL Season
    """
    import numpy as np
    from src.analytics.transformations import build_team_dataset

    logger.info("Building team intelligence dataset for Power BI.")

    matches = pd.read_parquet(STAGING_DIR / "match_info_processed.parquet")
    deliveries = pd.read_parquet(STAGING_DIR / "deliveries_processed.parquet")

    # Expand matches to team level
    team_df = build_team_dataset(matches)

    # Resolve super overs (ties)
    super_over_ids = set(deliveries[deliveries["innings"] > 2]["match_id"].unique())

    # Resolve player of match teams
    batters = deliveries[['match_id', 'striker', 'batting_team']].rename(columns={'striker': 'player', 'batting_team': 'team'})
    non_batters = deliveries[['match_id', 'non_striker', 'batting_team']].rename(columns={'non_striker': 'player', 'batting_team': 'team'})
    bowlers = deliveries[['match_id', 'bowler', 'bowling_team']].rename(columns={'bowler': 'player', 'bowling_team': 'team'})
    pm_team = pd.concat([batters, non_batters, bowlers]).drop_duplicates()

    matches_with_pom = matches[['match_id', 'player_of_match']].dropna()
    pom_resolved = matches_with_pom.merge(pm_team, left_on=['match_id', 'player_of_match'], right_on=['match_id', 'player'], how='left')
    pom_resolved_map = pom_resolved.set_index(['match_id', 'player_of_match'])['team'].to_dict()

    # Calculate indicator columns
    team_df['is_toss_winner'] = team_df['toss_winner'] == team_df['team']
    team_df['batting_first'] = (
        (team_df['is_toss_winner'] & (team_df['toss_decision'] == 'bat')) |
        (~team_df['is_toss_winner'] & (team_df['toss_decision'] == 'field'))
    )
    team_df['chasing'] = ~team_df['batting_first']

    team_df['is_win'] = (team_df['winner'] == team_df['team']).astype(int)
    team_df['is_loss'] = ((team_df['winner'] != team_df['team']) & team_df['winner'].notna()).astype(int)
    team_df['is_tie'] = team_df['match_id'].isin(super_over_ids).astype(int)
    team_df['is_no_result'] = ((~team_df['match_id'].isin(super_over_ids)) & team_df['winner'].isna()).astype(int)

    team_df['is_toss_win'] = team_df['is_toss_winner'].astype(int)
    team_df['is_toss_loss'] = (~team_df['is_toss_winner']).astype(int)

    team_df['chose_bat_first_ind'] = (team_df['is_toss_winner'] & (team_df['toss_decision'] == 'bat')).astype(int)
    team_df['chose_field_first_ind'] = (team_df['is_toss_winner'] & (team_df['toss_decision'] == 'field')).astype(int)
    team_df['toss_conversion_win_ind'] = (team_df['is_toss_winner'] & (team_df['winner'] == team_df['team'])).astype(int)

    team_df['batting_first_ind'] = team_df['batting_first'].astype(int)
    team_df['win_batting_first_ind'] = (team_df['batting_first'] & (team_df['winner'] == team_df['team'])).astype(int)

    team_df['chasing_ind'] = team_df['chasing'].astype(int)
    team_df['win_chasing_ind'] = (team_df['chasing'] & (team_df['winner'] == team_df['team'])).astype(int)

    team_df['win_by_runs_ind'] = ((team_df['winner'] == team_df['team']) & (team_df['winner_runs'].notna()) & (team_df['winner_runs'] > 0)).astype(int)
    team_df['win_by_wickets_ind'] = ((team_df['winner'] == team_df['team']) & (team_df['winner_wickets'].notna()) & (team_df['winner_wickets'] > 0)).astype(int)

    # Cast runs/wickets margins to numeric, replace NaN with 0
    team_df['winner_runs'] = pd.to_numeric(team_df['winner_runs'], errors='coerce').fillna(0).astype(int)
    team_df['winner_wickets'] = pd.to_numeric(team_df['winner_wickets'], errors='coerce').fillna(0).astype(int)

    team_df['run_win_margin'] = np.where(team_df['winner'] == team_df['team'], team_df['winner_runs'], 0)
    team_df['wicket_win_margin'] = np.where(team_df['winner'] == team_df['team'], team_df['winner_wickets'], 0)
    team_df['run_loss_margin'] = np.where((team_df['winner'] != team_df['team']) & team_df['winner'].notna(), team_df['winner_runs'], 0)
    team_df['wicket_loss_margin'] = np.where((team_df['winner'] != team_df['team']) & team_df['winner'].notna(), team_df['winner_wickets'], 0)

    def get_pom_team(row):
        pom = row['player_of_match']
        mid = row['match_id']
        if pd.isna(pom):
            return None
        return pom_resolved_map.get((mid, pom), None)

    team_df['pom_team'] = team_df.apply(get_pom_team, axis=1)
    team_df['is_pom_award'] = (team_df['pom_team'] == team_df['team']).astype(int)

    # Base aggregation by ['team', 'season']
    agg_df = team_df.groupby(['team', 'season']).agg(
        matches_played=('match_id', 'count'),
        wins=('is_win', 'sum'),
        losses=('is_loss', 'sum'),
        ties=('is_tie', 'sum'),
        no_results=('is_no_result', 'sum'),
        toss_wins=('is_toss_win', 'sum'),
        toss_losses=('is_toss_loss', 'sum'),
        chose_bat_first=('chose_bat_first_ind', 'sum'),
        chose_field_first=('chose_field_first_ind', 'sum'),
        toss_conversion_wins=('toss_conversion_win_ind', 'sum'),
        matches_batting_first=('batting_first_ind', 'sum'),
        wins_batting_first=('win_batting_first_ind', 'sum'),
        matches_chasing=('chasing_ind', 'sum'),
        wins_chasing=('win_chasing_ind', 'sum'),
        venues_played=('venue', 'nunique'),
        wins_by_runs=('win_by_runs_ind', 'sum'),
        wins_by_wickets=('win_by_wickets_ind', 'sum'),
        biggest_run_win=('run_win_margin', 'max'),
        biggest_wicket_win=('wicket_win_margin', 'max'),
        biggest_run_loss=('run_loss_margin', 'max'),
        biggest_wicket_loss=('wicket_loss_margin', 'max'),
        player_of_match_awards=('is_pom_award', 'sum'),
        first_match_date=('date', 'min'),
        last_match_date=('date', 'max'),
    ).reset_index()

    # Favourite Venue
    wins_df = team_df[team_df['is_win'] == 1]
    venue_wins = wins_df.groupby(['team', 'season', 'venue']).size().reset_index(name='wins_count')
    venue_wins = venue_wins.sort_values(by=['team', 'season', 'wins_count', 'venue'], ascending=[True, True, False, True])
    fav_venue = venue_wins.groupby(['team', 'season']).first().reset_index()
    fav_venue = fav_venue.rename(columns={'venue': 'favourite_venue', 'wins_count': 'favourite_venue_wins'})

    # Toughest Venue
    losses_df = team_df[team_df['is_loss'] == 1]
    venue_losses = losses_df.groupby(['team', 'season', 'venue']).size().reset_index(name='losses_count')
    venue_losses = venue_losses.sort_values(by=['team', 'season', 'losses_count', 'venue'], ascending=[True, True, False, True])
    tough_venue = venue_losses.groupby(['team', 'season']).first().reset_index()
    tough_venue = tough_venue.rename(columns={'venue': 'toughest_venue', 'losses_count': 'toughest_venue_losses'})

    # Merge venue stats
    final_df = agg_df.merge(fav_venue[['team', 'season', 'favourite_venue', 'favourite_venue_wins']], on=['team', 'season'], how='left')
    final_df = final_df.merge(tough_venue[['team', 'season', 'toughest_venue', 'toughest_venue_losses']], on=['team', 'season'], how='left')

    # Fill NaNs
    final_df['favourite_venue_wins'] = final_df['favourite_venue_wins'].fillna(0).astype(int)
    final_df['toughest_venue_losses'] = final_df['toughest_venue_losses'].fillna(0).astype(int)
    final_df['favourite_venue'] = final_df['favourite_venue'].fillna("")
    final_df['toughest_venue'] = final_df['toughest_venue'].fillna("")

    # Schema Column order
    columns_order = [
        'team', 'season', 'matches_played', 'wins', 'losses', 'ties', 'no_results',
        'toss_wins', 'toss_losses', 'chose_bat_first', 'chose_field_first', 'toss_conversion_wins',
        'matches_batting_first', 'wins_batting_first', 'matches_chasing', 'wins_chasing',
        'venues_played', 'favourite_venue', 'favourite_venue_wins', 'toughest_venue', 'toughest_venue_losses',
        'wins_by_runs', 'wins_by_wickets', 'biggest_run_win', 'biggest_wicket_win',
        'biggest_run_loss', 'biggest_wicket_loss', 'player_of_match_awards', 'first_match_date', 'last_match_date'
    ]
    final_df = final_df[columns_order]

    # Convert date columns to datetime64[ns] format
    final_df['first_match_date'] = pd.to_datetime(final_df['first_match_date'])
    final_df['last_match_date'] = pd.to_datetime(final_df['last_match_date'])

    # Cast integer columns to int type
    int_cols = [
        'season', 'matches_played', 'wins', 'losses', 'ties', 'no_results',
        'toss_wins', 'toss_losses', 'chose_bat_first', 'chose_field_first', 'toss_conversion_wins',
        'matches_batting_first', 'wins_batting_first', 'matches_chasing', 'wins_chasing',
        'venues_played', 'favourite_venue_wins', 'toughest_venue_losses',
        'wins_by_runs', 'wins_by_wickets', 'biggest_run_win', 'biggest_wicket_win',
        'biggest_run_loss', 'biggest_wicket_loss', 'player_of_match_awards'
    ]
    for col in int_cols:
        final_df[col] = final_df[col].astype(int)

    return final_df


def _compute_project_statistics() -> dict[str, Any]:
    """
    Compile final database and modeling statistics for presentation.
    """
    logger.info("Compiling overall project release statistics.")

    # Staging statistics
    matches_df = pd.read_parquet(STAGING_DIR / "match_info_processed.parquet")
    deliveries_df = pd.read_parquet(STAGING_DIR / "deliveries_processed.parquet")

    benchmark_df = pd.read_csv(MODELS_DIR / "benchmark_results.csv")
    benchmark_df_sorted = benchmark_df.sort_values(by="Test Accuracy", ascending=False)
    best_model = benchmark_df_sorted.iloc[0]["Model Name"]
    best_accuracy = benchmark_df_sorted.iloc[0]["Test Accuracy"]

    return {
        "Total Seasons": int(matches_df["season"].nunique()),
        "Total Matches": int(len(matches_df)),
        "Total Deliveries": int(len(deliveries_df)),
        "Total Venues": int(matches_df["venue"].nunique()),
        "Total Teams": int(matches_df["team1"].nunique()),
        "Best Classifier": best_model,
        "Best Model Accuracy": f"{best_accuracy * 100:.2f}%",
    }


def run_export_validation_pipeline() -> ReleasePipelineResult:
    """
    Execute the complete release workflow.
    """
    logger.info("Starting project release export and validation pipeline.")
    start_time = time.perf_counter()
    status = "FAILURE"
    export_summary: dict[str, Any] = {}
    project_stats: dict[str, Any] = {}

    try:
        # 1. Run all release checklist validations
        validation_summary = validate_project()

        # 2. Package release if validations pass
        if validation_summary["overall_status"] == "PASS":
            logger.info("Validation checklist passed. Proceeding with packaging.")

            # Make sure release folder starts clean, preserving the models directory
            if RELEASE_DIR.exists():
                for item in RELEASE_DIR.iterdir():
                    if item.name != "models":
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
            else:
                RELEASE_DIR.mkdir(parents=True, exist_ok=True)
            # Ensure models directory exists as well
            MODELS_DIR.mkdir(parents=True, exist_ok=True)

            counts = _package_release_artifacts()

            export_summary = {
                "Release Package Status": "SUCCESS",
                "Release Directory": str(RELEASE_DIR),
                "Staging Files Packaged": counts["staging"],
                "Warehouse Files Packaged": counts["warehouse"],
                "Analytics Files Packaged": counts["analytics"],
                "ML Deliverables Packaged": counts["ml"],
                "Power BI Datasets": counts["powerbi"],
            }

            # 3. Compile high-level release statistics
            project_stats = _compute_project_statistics()
            status = "SUCCESS"
        else:
            logger.warning("Validation checklist failed. Skipping release packaging.")
            export_summary = {
                "Release Package Status": "SKIPPED",
                "Reason": "Validation checklist failed",
            }

    except Exception as e:
        logger.exception("Release pipeline failed due to error: %s", e)
        export_summary = {
            "Release Package Status": "FAILED",
            "Error": str(e),
        }
        raise
    finally:
        execution_time = time.perf_counter() - start_time

    return ReleasePipelineResult(
        status=status,
        execution_time=execution_time,
        validation_summary=validation_summary,
        export_summary=export_summary,
        project_statistics=project_stats,
    )


__all__ = [
    "run_export_validation_pipeline",
]