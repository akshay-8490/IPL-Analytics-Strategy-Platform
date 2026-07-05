"""
Warehouse Star Schema Validator
===============================

Validate the integrity of the warehouse star schema.

Responsibilities
----------------
- Validate primary keys
- Validate foreign keys
- Detect orphan records
- Detect duplicate keys
- Produce warehouse validation report

Notes
-----
- Performs in-memory validation only.
- Does not interact with SQL.
"""

from __future__ import annotations

from typing import Any
import pandas as pd

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _validate_primary_key(
    *,
    dataframe: pd.DataFrame,
    key_column: str,
) -> dict[str, Any]:
    """
    Validate a primary key column.
    """
    duplicate_keys = dataframe[key_column].duplicated().sum()
    null_keys = dataframe[key_column].isna().sum()

    return {
        "primary_key": key_column,
        "duplicate_keys": int(duplicate_keys),
        "null_keys": int(null_keys),
        "is_valid": duplicate_keys == 0 and null_keys == 0,
    }


def _validate_foreign_key(
    *,
    fact_df: pd.DataFrame,
    dimension_df: pd.DataFrame,
    foreign_key: str,
    primary_key: str,
) -> dict[str, Any]:
    """
    Validate foreign key relationships.
    """
    orphan_count = (
        ~fact_df[foreign_key].isin(
            dimension_df[primary_key]
        )
    ).sum()

    return {
        "foreign_key": foreign_key,
        "orphan_records": int(orphan_count),
        "is_valid": orphan_count == 0,
    }


def _validation_summary(
    *,
    results: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate validation summary.
    """
    passed = sum(
        result["is_valid"]
        for result in results.values()
    )
    total = len(results)

    return {
        "total_checks": total,
        "passed_checks": passed,
        "failed_checks": total - passed,
        "warehouse_valid": passed == total,
    }


def validate_dimensions(
    *,
    dimensions: dict[str, pd.DataFrame],
) -> dict[str, dict[str, Any]]:
    """
    Validate warehouse dimensions.

    Parameters
    ----------
    dimensions : dict[str, pd.DataFrame]

    Returns
    -------
    dict
        Dimension primary key validation results.
    """
    logger.info("Validating warehouse dimensions.")

    return {
        "dim_season": _validate_primary_key(
            dataframe=dimensions["dim_season"],
            key_column="season_key",
        ),
        "dim_team": _validate_primary_key(
            dataframe=dimensions["dim_team"],
            key_column="team_key",
        ),
        "dim_player": _validate_primary_key(
            dataframe=dimensions["dim_player"],
            key_column="player_key",
        ),
        "dim_venue": _validate_primary_key(
            dataframe=dimensions["dim_venue"],
            key_column="venue_key",
        ),
        "dim_match": _validate_primary_key(
            dataframe=dimensions["dim_match"],
            key_column="match_key",
        ),
    }


def validate_fact_tables(
    *,
    dimensions: dict[str, pd.DataFrame],
    facts: dict[str, pd.DataFrame],
) -> dict[str, dict[str, Any]]:
    """
    Validate warehouse fact tables.

    Parameters
    ----------
    dimensions : dict[str, pd.DataFrame]
    facts : dict[str, pd.DataFrame]

    Returns
    -------
    dict
        Foreign-key validation results.
    """
    logger.info("Validating warehouse fact tables.")

    delivery_fact = facts["fact_delivery"]

    validation_results = {
        "match_key": _validate_foreign_key(
            fact_df=delivery_fact,
            dimension_df=dimensions["dim_match"],
            foreign_key="match_key",
            primary_key="match_key",
        ),
        "season_key": _validate_foreign_key(
            fact_df=delivery_fact,
            dimension_df=dimensions["dim_season"],
            foreign_key="season_key",
            primary_key="season_key",
        ),
        "batting_team_key": _validate_foreign_key(
            fact_df=delivery_fact,
            dimension_df=dimensions["dim_team"],
            foreign_key="batting_team_key",
            primary_key="team_key",
        ),
        "bowling_team_key": _validate_foreign_key(
            fact_df=delivery_fact,
            dimension_df=dimensions["dim_team"],
            foreign_key="bowling_team_key",
            primary_key="team_key",
        ),
        "batter_key": _validate_foreign_key(
            fact_df=delivery_fact,
            dimension_df=dimensions["dim_player"],
            foreign_key="batter_key",
            primary_key="player_key",
        ),
        "bowler_key": _validate_foreign_key(
            fact_df=delivery_fact,
            dimension_df=dimensions["dim_player"],
            foreign_key="bowler_key",
            primary_key="player_key",
        ),
        "non_striker_key": _validate_foreign_key(
            fact_df=delivery_fact,
            dimension_df=dimensions["dim_player"],
            foreign_key="non_striker_key",
            primary_key="player_key",
        ),
        "fielder_key": _validate_foreign_key(
            fact_df=delivery_fact,
            dimension_df=dimensions["dim_player"],
            foreign_key="fielder_key",
            primary_key="player_key",
        ),
    }

    logger.info("Fact table validation completed.")
    return validation_results


def validate_star_schema(
    *,
    dimensions: dict[str, pd.DataFrame],
    facts: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    """
    Validate the complete warehouse star schema.

    Parameters
    ----------
    dimensions : dict[str, pd.DataFrame]
    facts : dict[str, pd.DataFrame]

    Returns
    -------
    dict
        Complete validation report.
    """
    logger.info("Starting warehouse validation.")

    dimension_results = validate_dimensions(
        dimensions=dimensions,
    )

    fact_results = validate_fact_tables(
        dimensions=dimensions,
        facts=facts,
    )

    all_results = {
        **dimension_results,
        **fact_results,
    }

    summary = _validation_summary(
        results=all_results,
    )

    validation_report = {
        "dimensions": dimension_results,
        "facts": fact_results,
        "summary": summary,
    }

    logger.info("Warehouse validation completed.")
    return validation_report


__all__ = [
    "validate_dimensions",
    "validate_fact_tables",
    "validate_star_schema",
]