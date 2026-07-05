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

    # 2. Package Warehouse Parquets
    dimension_files = [
        DIMENSIONS_DIR / "dim_match.parquet",
        DIMENSIONS_DIR / "dim_team.parquet",
        DIMENSIONS_DIR / "dim_player.parquet",
        DIMENSIONS_DIR / "dim_venue.parquet",
        DIMENSIONS_DIR / "dim_season.parquet",
    ]
    for file_path in dimension_files:
        if file_path.exists():
            _copy_file_to_release(file_path, Path("data/processed/warehouse/dimensions"))
            counts["warehouse"] += 1

    fact_files = [
        FACTS_DIR / "fact_match.parquet",
        FACTS_DIR / "fact_player_match.parquet",
        FACTS_DIR / "fact_delivery.parquet",
    ]
    for file_path in fact_files:
        if file_path.exists():
            _copy_file_to_release(file_path, Path("data/processed/warehouse/facts"))
            counts["warehouse"] += 1

    # 3. Package Analytics Mart
    # Copy executive summary
    exec_summary_file = ANALYTICS_DATA_DIR / "executive/executive_summary.json"
    if exec_summary_file.exists():
        _copy_file_to_release(exec_summary_file, Path("data/analytics/executive"))
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
    ml_files = [
        MODELS_DIR / "benchmark_results.csv",
        MODELS_DIR / "classification_report.json",
        MODELS_DIR / "feature_importance.csv",
        MODELS_DIR / "confusion_matrix.csv",
    ]
    for file_path in ml_files:
        if file_path.exists():
            _copy_file_to_release(file_path, Path("models"))
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

            # Make sure release folder starts clean
            if RELEASE_DIR.exists():
                shutil.rmtree(RELEASE_DIR)
            RELEASE_DIR.mkdir(parents=True, exist_ok=True)

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