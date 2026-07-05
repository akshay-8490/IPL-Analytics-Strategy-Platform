"""
mysql_loader.py

Utilities for loading warehouse DataFrames into the MySQL data warehouse.

Responsibilities
----------------
- Bulk load dimension tables
- Bulk load fact tables
- Handle transactions
- Perform chunked inserts
- Verify successful loading

This module intentionally contains no business logic and assumes that
all warehouse DataFrames have already been validated.
"""

from __future__ import annotations

import logging
from typing import Dict

import pandas as pd
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from mysql.connector import Error

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

DEFAULT_BATCH_SIZE = 5_000

DIMENSION_LOAD_ORDER = (
    "dim_season",
    "dim_team",
    "dim_player",
    "dim_venue",
    "dim_match",
)

FACT_LOAD_ORDER = (
    "fact_match",
    "fact_player_match",
    "fact_delivery",
)

__all__ = [
    "load_dimension",
    "load_fact_table",
    "load_warehouse",
    "verify_load",
    "get_table_row_count",
]

def _validate_table_exists(
    *,
    connection: MySQLConnection,
    table_name: str,
) -> None:
    """
    Validate that the target table exists.

    Parameters
    ----------
    connection : MySQLConnection
        Active MySQL connection.

    table_name : str
        Table to validate.

    Raises
    ------
    ValueError
        If the table does not exist.
    """

    logger.debug(
        "Validating existence of table '%s'.",
        table_name,
    )

    cursor: MySQLCursor = connection.cursor()

    try:
        cursor.execute(
            """
            SHOW TABLES LIKE %s
            """,
            (table_name,),
        )

        if cursor.fetchone() is None:
            raise ValueError(
                f"Table '{table_name}' does not exist."
            )

    finally:
        cursor.close()

def _prepare_dataframe(
    *,
    dataframe: pd.DataFrame,
) -> tuple[list[str], list[tuple]]:
    """
    Prepare a DataFrame for MySQL insertion.

    Parameters
    ----------
    dataframe : pd.DataFrame
        Warehouse DataFrame.

    Returns
    -------
    tuple[list[str], list[tuple]]
        Column names and row tuples ready for executemany().
    """

    logger.debug(
        "Preparing DataFrame with %d rows for loading.",
        len(dataframe),
    )

    if dataframe.empty:
        return [], []

    prepared_df = dataframe.copy()

    # Convert datetime columns to native Python datetime objects.
    datetime_columns = prepared_df.select_dtypes(
        include=["datetime64[ns]", "datetimetz"],
    ).columns

    for column in datetime_columns:
        prepared_df[column] = prepared_df[column].apply(
            lambda value: (
                value.to_pydatetime()
                if pd.notnull(value)
                else None
            )
        )

    # Cast to object type and replace NA/nan with None
    prepared_df = prepared_df.astype(object)
    prepared_df = prepared_df.where(
        pd.notnull(prepared_df),
        None,
    )

    columns = prepared_df.columns.tolist()

    # Convert values to native Python types in list of tuples
    import numpy as np

    def to_native(val):
        if isinstance(val, (np.integer, np.int64, np.int32)):
            return int(val)
        if isinstance(val, (np.floating, np.float64, np.float32)):
            return float(val)
        if isinstance(val, np.bool_):
            return bool(val)
        if pd.isna(val):
            return None
        return val

    rows = []
    for r in prepared_df.itertuples(index=False, name=None):
        rows.append(tuple(to_native(val) for val in r))

    logger.debug(
        "Prepared %d rows for insertion.",
        len(rows),
    )

    return columns, rows

def _load_chunk(
    *,
    cursor: MySQLCursor,
    insert_sql: str,
    rows: list[tuple],
) -> None:
    """
    Load a single batch of rows into MySQL.

    Parameters
    ----------
    cursor : MySQLCursor
        Active cursor.

    insert_sql : str
        Parameterized INSERT statement.

    rows : list[tuple]
        Batch of rows to insert.
    """

    if not rows:
        return

    cursor.executemany(
        insert_sql,
        rows,
    )

def _execute_insert(
    *,
    connection: MySQLConnection,
    table_name: str,
    dataframe: pd.DataFrame,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    """
    Execute a bulk insert into a MySQL table.

    Parameters
    ----------
    connection : MySQLConnection
        Active MySQL connection.

    table_name : str
        Destination table.

    dataframe : pd.DataFrame
        DataFrame to insert.

    batch_size : int, default=DEFAULT_BATCH_SIZE
        Number of rows inserted per batch.

    Returns
    -------
    int
        Number of inserted rows.
    """

    logger.info(
        "Loading %d rows into '%s'.",
        len(dataframe),
        table_name,
    )

    _validate_table_exists(
        connection=connection,
        table_name=table_name,
    )

    columns, rows = _prepare_dataframe(
        dataframe=dataframe,
    )

    if not rows:
        logger.warning(
            "No rows available for table '%s'.",
            table_name,
        )
        return 0

    placeholders = ", ".join(["%s"] * len(columns))

    column_sql = ", ".join(
        f"`{column}`"
        for column in columns
    )

    insert_sql = (
        f"INSERT INTO `{table_name}` "
        f"({column_sql}) "
        f"VALUES ({placeholders})"
    )

    cursor: MySQLCursor = connection.cursor()

    try:

        total_rows = len(rows)

        for start in range(
            0,
            total_rows,
            batch_size,
        ):

            batch = rows[start:start + batch_size]

            _load_chunk(
                cursor=cursor,
                insert_sql=insert_sql,
                rows=batch,
            )

        connection.commit()

        logger.info(
            "Successfully loaded %d rows into '%s'.",
            total_rows,
            table_name,
        )

        return total_rows

    except Error:

        connection.rollback()

        logger.exception(
            "Failed loading table '%s'. Transaction rolled back.",
            table_name,
        )

        raise

    finally:

        cursor.close()

def load_dimension(
    *,
    connection: MySQLConnection,
    table_name: str,
    dataframe: pd.DataFrame,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    """
    Load a warehouse dimension into MySQL.

    Parameters
    ----------
    connection : MySQLConnection
        Active database connection.

    table_name : str
        Dimension table name.

    dataframe : pd.DataFrame
        Dimension DataFrame.

    batch_size : int, default=DEFAULT_BATCH_SIZE
        Batch size for bulk insertion.

    Returns
    -------
    int
        Number of inserted rows.
    """

    logger.info(
        "Loading dimension '%s'.",
        table_name,
    )

    return _execute_insert(
        connection=connection,
        table_name=table_name,
        dataframe=dataframe,
        batch_size=batch_size,
    )

def load_fact_table(
    *,
    connection: MySQLConnection,
    table_name: str,
    dataframe: pd.DataFrame,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    """
    Load a warehouse fact table into MySQL.

    Parameters
    ----------
    connection : MySQLConnection
        Active database connection.

    table_name : str
        Fact table name.

    dataframe : pd.DataFrame
        Fact DataFrame.

    batch_size : int, default=DEFAULT_BATCH_SIZE
        Batch size for bulk insertion.

    Returns
    -------
    int
        Number of inserted rows.
    """

    logger.info(
        "Loading fact table '%s'.",
        table_name,
    )

    return _execute_insert(
        connection=connection,
        table_name=table_name,
        dataframe=dataframe,
        batch_size=batch_size,
    )

def get_table_row_count(
    *,
    connection: MySQLConnection,
    table_name: str,
) -> int:
    """
    Return the number of rows in a database table.

    Parameters
    ----------
    connection : MySQLConnection
        Active database connection.

    table_name : str
        Target table.

    Returns
    -------
    int
        Row count.
    """

    _validate_table_exists(
        connection=connection,
        table_name=table_name,
    )

    cursor: MySQLCursor = connection.cursor()

    try:

        cursor.execute(
            f"SELECT COUNT(*) FROM `{table_name}`"
        )

        row_count = cursor.fetchone()[0]

        logger.debug(
            "Table '%s' contains %d rows.",
            table_name,
            row_count,
        )

        return row_count

    finally:
        cursor.close()

def verify_load(
    *,
    connection: MySQLConnection,
    table_name: str,
    dataframe: pd.DataFrame,
) -> bool:
    """
    Verify that all DataFrame rows were loaded successfully.

    Parameters
    ----------
    connection : MySQLConnection
        Active database connection.

    table_name : str
        Target table.

    dataframe : pd.DataFrame
        Source DataFrame.

    Returns
    -------
    bool
        True if row counts match.
    """

    expected = len(dataframe)

    actual = get_table_row_count(
        connection=connection,
        table_name=table_name,
    )

    if expected != actual:

        logger.error(
            "Verification failed for '%s'. "
            "Expected %d rows but found %d.",
            table_name,
            expected,
            actual,
        )

        return False

    logger.info(
        "Verified '%s' (%d rows).",
        table_name,
        actual,
    )

    return True

def load_warehouse(
    *,
    connection: MySQLConnection,
    dimensions: Dict[str, pd.DataFrame],
    facts: Dict[str, pd.DataFrame],
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> Dict[str, int]:
    """
    Load the complete warehouse into MySQL.

    Parameters
    ----------
    connection : MySQLConnection
        Active MySQL connection.

    dimensions : dict[str, pd.DataFrame]
        Dimension DataFrames keyed by table name.

    facts : dict[str, pd.DataFrame]
        Fact DataFrames keyed by table name.

    batch_size : int, default=DEFAULT_BATCH_SIZE
        Bulk insert batch size.

    Returns
    -------
    dict[str, int]
        Number of inserted rows per table.
    """

    logger.info(
        "Starting warehouse loading process."
    )

    load_summary: Dict[str, int] = {}

    # --------------------------------------------------
    # Load Dimensions
    # --------------------------------------------------

    for table_name in DIMENSION_LOAD_ORDER:

        dataframe = dimensions.get(table_name)

        if dataframe is None:
            raise ValueError(
                f"Missing dimension '{table_name}'."
            )

        inserted = load_dimension(
            connection=connection,
            table_name=table_name,
            dataframe=dataframe,
            batch_size=batch_size,
        )

        verify_load(
            connection=connection,
            table_name=table_name,
            dataframe=dataframe,
        )

        load_summary[table_name] = inserted

    # --------------------------------------------------
    # Load Facts
    # --------------------------------------------------

    for table_name in FACT_LOAD_ORDER:

        dataframe = facts.get(table_name)

        if dataframe is None:
            raise ValueError(
                f"Missing fact table '{table_name}'."
            )

        inserted = load_fact_table(
            connection=connection,
            table_name=table_name,
            dataframe=dataframe,
            batch_size=batch_size,
        )

        verify_load(
            connection=connection,
            table_name=table_name,
            dataframe=dataframe,
        )

        load_summary[table_name] = inserted

    logger.info(
        "Warehouse successfully loaded."
    )

    return load_summary