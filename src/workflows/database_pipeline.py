"""
database_pipeline.py

Workflow for constructing and loading the IPL
Analytics Warehouse into MySQL.

Responsibilities
----------------
- Load engineered datasets
- Build warehouse
- Create schema
- Load warehouse
- Validate warehouse

This module contains orchestration only.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import time
from typing import Dict, Any

import pandas as pd
from mysql.connector.connection import MySQLConnection

from config.config import (
    DIMENSIONS_DIR,
    FACTS_DIR,
)

from src.database import (
    close_connection,
    create_connection,
    create_schema,
    drop_schema,
    load_warehouse,
)
from src.warehouse import (
    assign_surrogate_keys,
    build_dimensions,
    build_fact_tables,
    validate_star_schema,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatabasePipelineResult:
    """
    Result of the database pipeline execution.
    """
    load_summary: Dict[str, int]
    validation_summary: Dict[str, Any]
    execution_time: float
    database_name: str
    status: str


__all__ = [
    "run_database_pipeline",
    "DatabasePipelineResult",
]


def _load_processed_data(
    *,
    matches_path: str,
    deliveries_path: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load engineered datasets.

    Parameters
    ----------
    matches_path : str
    deliveries_path : str

    Returns
    -------
    tuple
        Matches and deliveries DataFrames.
    """
    logger.info("Loading engineered datasets.")

    matches_df = pd.read_parquet(matches_path)
    deliveries_df = pd.read_parquet(deliveries_path)

    # Standardize venue casing to prevent duplicate key violations in MySQL
    if "venue" in matches_df.columns:
        matches_df["venue"] = matches_df["venue"].replace(
            "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
            "Punjab Cricket Association Is Bindra Stadium, Mohali, Chandigarh"
        )
    if "venue" in deliveries_df.columns:
        deliveries_df["venue"] = deliveries_df["venue"].replace(
            "Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh",
            "Punjab Cricket Association Is Bindra Stadium, Mohali, Chandigarh"
        )

    # Standardize team name casing globally
    matches_df = matches_df.replace("Kings Xi Punjab", "Kings XI Punjab")
    deliveries_df = deliveries_df.replace("Kings Xi Punjab", "Kings XI Punjab")

    if "season" in deliveries_df.columns:
        from src.etl.normalizers import normalize_season
        deliveries_df["season"] = (
            deliveries_df["season"]
            .apply(normalize_season)
            .astype("Int64")
        )

    return matches_df, deliveries_df


def _build_warehouse(
    *,
    matches_df: pd.DataFrame,
    deliveries_df: pd.DataFrame,
) -> tuple[Dict[str, pd.DataFrame], Dict[str, pd.DataFrame]]:
    """
    Build warehouse dimensions and facts.
    """
    logger.info("Building warehouse.")

    dimensions = build_dimensions(
        matches_df=matches_df,
        deliveries_df=deliveries_df,
    )

    dimensions, lookup_maps = assign_surrogate_keys(
        dimensions=dimensions,
    )

    facts = build_fact_tables(
        deliveries_df=deliveries_df,
        lookup_maps=lookup_maps,
    )

    validate_star_schema(
        dimensions=dimensions,
        facts=facts,
    )

    return dimensions, facts


def _load_database(
    *,
    connection: MySQLConnection,
    dimensions: Dict[str, pd.DataFrame],
    facts: Dict[str, pd.DataFrame],
) -> Dict[str, int]:
    """
    Create the database schema and load the warehouse.

    Parameters
    ----------
    connection : MySQLConnection
        Active database connection.
    dimensions : dict[str, pd.DataFrame]
        Warehouse dimensions.
    facts : dict[str, pd.DataFrame]
        Warehouse fact tables.

    Returns
    -------
    dict[str, int]
        Load summary.
    """
    logger.info("Dropping database schema if it exists.")
    try:
        drop_schema(connection=connection)
    except Exception as e:
        logger.warning("Could not drop database schema: %s", e)

    logger.info("Creating database schema.")
    create_schema(connection=connection)

    logger.info("Loading warehouse into MySQL.")
    return load_warehouse(
        connection=connection,
        dimensions=dimensions,
        facts=facts,
    )


def _run_validation(
    *,
    dimensions: Dict[str, pd.DataFrame],
    facts: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    """
    Validate the completed warehouse.

    Parameters
    ----------
    dimensions : dict[str, pd.DataFrame]
    facts : dict[str, pd.DataFrame]

    Returns
    -------
    dict[str, Any]
        Validation report.
    """
    logger.info("Running warehouse validation.")
    report = validate_star_schema(
        dimensions=dimensions,
        facts=facts,
    )
    logger.info("Warehouse validation completed.")
    return report


def run_database_pipeline(
    *,
    matches_path: str,
    deliveries_path: str,
) -> DatabasePipelineResult:
    """
    Execute the complete database pipeline.

    Parameters
    ----------
    matches_path : str
        Path to engineered match dataset.
    deliveries_path : str
        Path to engineered delivery dataset.

    Returns
    -------
    DatabasePipelineResult
        Encapsulated execution metrics and summaries.
    """
    logger.info("Starting database pipeline.")
    start_time = time.perf_counter()

    connection = create_connection()
    try:
        matches_df, deliveries_df = _load_processed_data(
            matches_path=matches_path,
            deliveries_path=deliveries_path,
        )

        dimensions, facts = _build_warehouse(
            matches_df=matches_df,
            deliveries_df=deliveries_df,
        )

        load_summary = _load_database(
            connection=connection,
            dimensions=dimensions,
            facts=facts,
        )

        validation_report = _run_validation(
            dimensions=dimensions,
            facts=facts,
        )

        logger.info("Saving conformed dimensions and facts to warehouse directory.")
        for name, df in dimensions.items():
            df.to_parquet(DIMENSIONS_DIR / f"{name}.parquet", index=False)
        for name, df in facts.items():
            df.to_parquet(FACTS_DIR / f"{name}.parquet", index=False)

        execution_time = time.perf_counter() - start_time
        from config.settings import MYSQL_DATABASE

        logger.info("Database pipeline completed successfully.")
        return DatabasePipelineResult(
            load_summary=load_summary,
            validation_summary=validation_report,
            execution_time=execution_time,
            database_name=MYSQL_DATABASE,
            status="SUCCESS",
        )

    finally:
        close_connection(connection)
