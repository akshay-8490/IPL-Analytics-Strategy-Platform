"""
Database validation queries.

This module contains functions that generate SQL queries used for validating the integrity
of the IPL Analytics Warehouse data, checking for duplicate keys, null values, and orphan foreign keys.
"""

from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def get_row_count_query(
    table_name: str,
) -> str:
    """
    Build a query that returns the number of rows in a table.
    """
    return f"SELECT COUNT(*) AS row_count FROM `{table_name}`;"


def get_null_count_query(
    table_name: str,
    column_name: str,
) -> str:
    """
    Build a query that counts NULL values for a column.
    """
    return f"SELECT COUNT(*) AS null_count FROM `{table_name}` WHERE `{column_name}` IS NULL;"


def get_duplicate_keys_query(
    table_name: str,
    key_columns: list[str],
) -> str:
    """
    Build a query that detects duplicate composite keys.
    """
    columns = ", ".join(f"`{column}`" for column in key_columns)
    return f"""
        SELECT
            {columns},
            COUNT(*) AS duplicate_count
        FROM `{table_name}`
        GROUP BY {columns}
        HAVING COUNT(*) > 1;
    """


def get_missing_fk_query(
    *,
    fact_table: str,
    fact_key: str,
    dimension_table: str,
    dimension_key: str,
) -> str:
    """
    Build a query that detects orphan foreign keys.
    """
    return f"""
        SELECT
            COUNT(*) AS orphan_records
        FROM `{fact_table}` f
        LEFT JOIN `{dimension_table}` d
            ON f.`{fact_key}` = d.`{dimension_key}`
        WHERE d.`{dimension_key}` IS NULL;
    """


def get_dimension_validation_queries(
    *,
    table_name: str,
    primary_key: str,
) -> Dict[str, str]:
    """
    Build the standard validation queries for a warehouse dimension.
    """
    logger.debug(
        "Building validation queries for dimension '%s'.",
        table_name,
    )
    return {
        "row_count": get_row_count_query(table_name),
        "duplicate_keys": get_duplicate_keys_query(
            table_name=table_name,
            key_columns=[primary_key],
        ),
        "null_primary_key": get_null_count_query(table_name, primary_key),
    }


def get_fact_validation_queries(
    *,
    table_name: str,
    primary_keys: list[str],
    foreign_keys: Dict[str, tuple[str, str]],
) -> Dict[str, str]:
    """
    Build validation queries for a warehouse fact table.
    """
    logger.debug(
        "Building validation queries for fact '%s'.",
        table_name,
    )
    queries = {
        "row_count": get_row_count_query(table_name),
        "duplicate_keys": get_duplicate_keys_query(
            table_name=table_name,
            key_columns=primary_keys,
        ),
    }

    for fact_key, (dimension_table, dimension_key) in foreign_keys.items():
        queries[f"{fact_key}_fk"] = get_missing_fk_query(
            fact_table=table_name,
            fact_key=fact_key,
            dimension_table=dimension_table,
            dimension_key=dimension_key,
        )

    return queries


__all__ = [
    "get_row_count_query",
    "get_null_count_query",
    "get_duplicate_keys_query",
    "get_missing_fk_query",
    "get_dimension_validation_queries",
    "get_fact_validation_queries",
]
