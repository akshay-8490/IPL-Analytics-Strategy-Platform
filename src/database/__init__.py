"""
Database package init.

Exposes connection, schema creation, data loading, and query generation utilities.
"""

from __future__ import annotations

from .connection import (
    close_connection,
    create_connection,
    test_connection,
)
from .schema import (
    create_schema,
    drop_schema,
)
from .mysql_loader import (
    get_table_row_count,
    load_dimension,
    load_fact_table,
    load_warehouse,
    verify_load,
)
from .validation_queries import (
    get_dimension_validation_queries,
    get_duplicate_keys_query,
    get_fact_validation_queries,
    get_missing_fk_query,
    get_null_count_query,
    get_row_count_query,
)
from .analytics_queries import (
    get_analytics_queries,
    get_match_summary_query,
    get_player_summary_query,
    get_season_summary_query,
    get_team_summary_query,
)

__all__ = [
    # Connection
    "create_connection",
    "test_connection",
    "close_connection",
    # Schema
    "create_schema",
    "drop_schema",
    # Loader
    "load_dimension",
    "load_fact_table",
    "load_warehouse",
    "verify_load",
    "get_table_row_count",
    # Validation Queries
    "get_row_count_query",
    "get_null_count_query",
    "get_duplicate_keys_query",
    "get_missing_fk_query",
    "get_dimension_validation_queries",
    "get_fact_validation_queries",
    # Analytics Queries
    "get_match_summary_query",
    "get_team_summary_query",
    "get_player_summary_query",
    "get_season_summary_query",
    "get_analytics_queries",
]
