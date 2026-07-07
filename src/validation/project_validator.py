"""
project_validator.py

This module validates the entire project release by performing a series of sanity
checks on the processed datasets, MySQL warehouse flat-file outputs, Gold Layer
analytics datasets, machine learning deliverables, and packaging directories.
"""

from __future__ import annotations

import json
import os
from typing import Any

import pandas as pd

from config.config import (
    ANALYTICS_DATA_DIR,
    DIMENSIONS_DIR,
    FACTS_DIR,
    MODELS_DIR,
    STAGING_DIR,
    WAREHOUSE_DIR,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _validate_processed_data() -> dict[str, Any]:
    """
    Validate processed data layer files.
    """
    expected_files = [
        STAGING_DIR / "match_info_processed.parquet",
        STAGING_DIR / "deliveries_processed.parquet",
        STAGING_DIR / "match_features.parquet",
        STAGING_DIR / "player_features.parquet",
    ]

    passed = 0
    failed = 0
    missing = []

    for file_path in expected_files:
        name = file_path.name
        # Check 1: Existence
        if not file_path.exists():
            failed += 1
            missing.append(f"{name} (missing)")
            continue
        passed += 1

        # Check 2 & 3: Readability & non-empty
        try:
            df = pd.read_parquet(file_path)
            if df.empty:
                failed += 1
                missing.append(f"{name} (empty)")
            else:
                passed += 2
        except Exception as e:
            failed += 2
            missing.append(f"{name} (corrupt/unreadable: {str(e)})")

    status = "FAIL" if failed > 0 else "PASS"
    return {
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "missing": missing,
    }


def _validate_warehouse() -> dict[str, Any]:
    """
    Validate warehouse dimensions and facts flat files.
    """
    expected_files = [
        # Parquets
        DIMENSIONS_DIR / "dim_match.parquet",
        DIMENSIONS_DIR / "dim_team.parquet",
        DIMENSIONS_DIR / "dim_player.parquet",
        DIMENSIONS_DIR / "dim_venue.parquet",
        DIMENSIONS_DIR / "dim_season.parquet",
        FACTS_DIR / "fact_match.parquet",
        FACTS_DIR / "fact_player_match.parquet",
        FACTS_DIR / "fact_delivery.parquet",
        
        # CSVs
        DIMENSIONS_DIR / "dim_match.csv",
        DIMENSIONS_DIR / "dim_team.csv",
        DIMENSIONS_DIR / "dim_player.csv",
        DIMENSIONS_DIR / "dim_venue.csv",
        DIMENSIONS_DIR / "dim_season.csv",
        FACTS_DIR / "fact_match.csv",
        FACTS_DIR / "fact_player_match.csv",
        FACTS_DIR / "fact_delivery.csv",
    ]

    passed = 0
    failed = 0
    missing = []

    for file_path in expected_files:
        name = f"{file_path.parent.name}/{file_path.name}"
        # Check 1: Existence
        if not file_path.exists():
            failed += 1
            missing.append(f"{name} (missing)")
            continue
        passed += 1

        # Check 2 & 3: Readability & non-empty
        try:
            if file_path.suffix == ".parquet":
                df = pd.read_parquet(file_path)
            else:
                df = pd.read_csv(file_path)
            if df.empty:
                failed += 1
                missing.append(f"{name} (empty)")
            else:
                passed += 2
        except Exception as e:
            failed += 2
            missing.append(f"{name} (corrupt/unreadable: {str(e)})")

    status = "FAIL" if failed > 0 else "PASS"
    return {
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "missing": missing,
    }


def _validate_analytics() -> dict[str, Any]:
    """
    Validate Analytics Data Mart structure and exports.
    """
    expected_dirs = [
        ANALYTICS_DATA_DIR / "executive",
        ANALYTICS_DATA_DIR / "season",
        ANALYTICS_DATA_DIR / "team",
        ANALYTICS_DATA_DIR / "venue",
        ANALYTICS_DATA_DIR / "player",
        ANALYTICS_DATA_DIR / "match",
        ANALYTICS_DATA_DIR / "head_to_head",
    ]

    expected_files = {
        "executive": ["executive_summary.json", "season_summary.csv"],
        "season": ["margins.parquet", "matches.parquet", "outcomes.parquet", "player_of_match.parquet", "teams.parquet", "toss.parquet", "venues.parquet"],
        "team": ["margins.parquet", "participation.parquet", "season.parquet", "toss.parquet", "venue.parquet", "wins.parquet"],
        "venue": ["margins.parquet", "matches.parquet", "season.parquet", "teams.parquet", "toss.parquet"],
        "player": ["awards.parquet", "match_type.parquet", "season.parquet", "team.parquet", "venue.parquet"],
        "match": ["margins.parquet", "match_types.parquet", "results.parquet", "toss.parquet", "toss_advantage.parquet"],
        "head_to_head": ["margins.parquet", "matches.parquet", "season.parquet", "venue.parquet", "wins.parquet"],
    }

    passed = 0
    failed = 0
    missing = []

    # Validate directories
    for dir_path in expected_dirs:
        if not dir_path.exists() or not dir_path.is_dir():
            failed += 1
            missing.append(f"Directory {dir_path.name} (missing/invalid)")
        else:
            passed += 1

    # Validate files
    for domain, files in expected_files.items():
        domain_dir = ANALYTICS_DATA_DIR / domain
        if not domain_dir.exists():
            failed += len(files) * 3
            for f in files:
                missing.append(f"analytics/{domain}/{f} (directory missing)")
            continue

        for filename in files:
            file_path = domain_dir / filename
            full_name = f"analytics/{domain}/{filename}"

            # Check 1: Existence
            if not file_path.exists():
                failed += 1
                missing.append(f"{full_name} (missing)")
                continue
            passed += 1

            # Check 2 & 3: Readability & non-empty
            try:
                if file_path.suffix == ".json":
                    with file_path.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                    if not data:
                        failed += 1
                        missing.append(f"{full_name} (empty json)")
                    else:
                        passed += 2
                elif file_path.suffix == ".csv":
                    df = pd.read_csv(file_path)
                    if df.empty:
                        failed += 1
                        missing.append(f"{full_name} (empty csv)")
                    else:
                        passed += 2
                else:
                    df = pd.read_parquet(file_path)
                    if df.empty:
                        failed += 1
                        missing.append(f"{full_name} (empty parquet)")
                    else:
                        passed += 2
            except Exception as e:
                failed += 2
                missing.append(f"{full_name} (corrupt/unreadable: {str(e)})")

    status = "FAIL" if failed > 0 else "PASS"
    return {
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "missing": missing,
    }


def _validate_machine_learning() -> dict[str, Any]:
    """
    Validate Machine Learning models directory deliverables.
    """
    expected_files = [
        MODELS_DIR / "benchmark_results.csv",
        MODELS_DIR / "classification_report.json",
        MODELS_DIR / "feature_importance.csv",
        MODELS_DIR / "confusion_matrix.csv",
    ]

    passed = 0
    failed = 0
    missing = []

    for file_path in expected_files:
        name = f"models/{file_path.name}"
        # Check 1: Existence
        if not file_path.exists():
            failed += 1
            missing.append(f"{name} (missing)")
            continue
        passed += 1

        # Check 2 & 3: Readability & non-empty
        try:
            if file_path.suffix == ".json":
                with file_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if not data:
                    failed += 1
                    missing.append(f"{name} (empty json)")
                else:
                    passed += 2
            else:
                df = pd.read_csv(file_path)
                if df.empty:
                    failed += 1
                    missing.append(f"{name} (empty csv)")
                else:
                    passed += 2
        except Exception as e:
            failed += 2
            missing.append(f"{name} (corrupt/unreadable: {str(e)})")

    status = "FAIL" if failed > 0 else "PASS"
    return {
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "missing": missing,
    }


def _validate_exports() -> dict[str, Any]:
    """
    Validate packaging release output directories.
    """
    expected_dirs = [
        ANALYTICS_DATA_DIR,
        WAREHOUSE_DIR,
        MODELS_DIR,
    ]

    passed = 0
    failed = 0
    missing = []

    for dir_path in expected_dirs:
        name = dir_path.name
        # Check 1: Existence
        if not dir_path.exists():
            failed += 1
            missing.append(f"{name} directory (missing)")
            continue
        passed += 1

        # Check 2: Is Directory
        if not dir_path.is_dir():
            failed += 1
            missing.append(f"{name} path (not a directory)")
            continue
        passed += 1

        # Check 3: Writeable
        if not os.access(dir_path, os.W_OK):
            failed += 1
            missing.append(f"{name} directory (read-only)")
        else:
            passed += 1

    status = "FAIL" if failed > 0 else "PASS"
    return {
        "status": status,
        "checks_passed": passed,
        "checks_failed": failed,
        "missing": missing,
    }


def _build_validation_summary(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """
    Combine all validation check reports into one aggregated release report.
    """
    summary: dict[str, Any] = {}
    total_passed = 0
    total_failed = 0

    for category, report in reports.items():
        summary[category] = report
        total_passed += report["checks_passed"]
        total_failed += report["checks_failed"]

    overall_status = "FAIL" if total_failed > 0 else "PASS"

    summary["overall_status"] = overall_status
    summary["checks_passed"] = total_passed
    summary["checks_failed"] = total_failed

    return summary


def validate_project() -> dict[str, Any]:
    """
    Run all category validations and build the final release summary checklist.
    """
    logger.info("Validating processed datasets...")
    processed_report = _validate_processed_data()

    logger.info("Validating warehouse artifacts...")
    warehouse_report = _validate_warehouse()

    logger.info("Validating analytics outputs...")
    analytics_report = _validate_analytics()

    logger.info("Validating machine learning outputs...")
    ml_report = _validate_machine_learning()

    logger.info("Validating export release packaging folders...")
    exports_report = _validate_exports()

    logger.info("Building validation summary...")
    reports = {
        "processed_data": processed_report,
        "warehouse": warehouse_report,
        "analytics": analytics_report,
        "machine_learning": ml_report,
        "exports": exports_report,
    }

    summary = _build_validation_summary(reports)

    if summary["overall_status"] == "PASS":
        logger.info("Project validation completed successfully.")
    else:
        logger.warning(
            "Project validation completed with failures: %d failed checks.",
            summary["checks_failed"],
        )

    return summary


__all__ = [
    "validate_project",
]
