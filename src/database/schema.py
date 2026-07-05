"""
Database schema management.

This module is responsible for creating and managing the
physical MySQL schema for the IPL Analytics & Strategy Platform.

Responsibilities
----------------
- Create the warehouse database
- Create warehouse tables
- Create indexes and constraints

This module intentionally does NOT:
- Load data
- Execute analytics queries
- Perform business transformations
"""

from __future__ import annotations

import logging

from mysql.connector import Error
from mysql.connector.connection import MySQLConnection

from config import MYSQL_DATABASE
from src.database.ddl import (
    get_dim_season_ddl,
    get_dim_team_ddl,
    get_dim_player_ddl,
    get_dim_venue_ddl,
    get_dim_match_ddl,
    get_fact_match_ddl,
    get_fact_player_match_ddl,
    get_fact_delivery_ddl,
    get_indexes_ddl,
)

logger = logging.getLogger(__name__)


def _execute_ddl(
    *,
    connection: MySQLConnection,
    sql: str,
    object_name: str,
) -> None:
    """
    Execute a DDL statement.
    """
    logger.info("Creating %s.", object_name)

    cursor = connection.cursor()
    try:
        cursor.execute(sql)
        connection.commit()
        logger.info("%s created successfully.", object_name)
    except Error as exc:
        connection.rollback()
        logger.exception("Failed to create %s.", object_name)
        raise RuntimeError(f"Unable to create {object_name}.") from exc
    finally:
        cursor.close()


def _create_database(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the warehouse database if it does not exist.
    """
    sql = f"""
    CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
    """

    _execute_ddl(
        connection=connection,
        sql=sql,
        object_name=f"database '{MYSQL_DATABASE}'",
    )


def _use_database(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Select the warehouse database.
    """
    logger.info("Selecting database '%s'.", MYSQL_DATABASE)

    cursor = connection.cursor()
    try:
        cursor.execute(f"USE `{MYSQL_DATABASE}`;")
        # Update connection object configuration to ensure reconnects use this database
        connection.database = MYSQL_DATABASE
        logger.info("Using database '%s'.", MYSQL_DATABASE)
    except Error as exc:
        logger.exception("Failed to select database '%s'.", MYSQL_DATABASE)
        raise RuntimeError(f"Unable to use database '{MYSQL_DATABASE}'.") from exc
    finally:
        cursor.close()


def _create_dim_season(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the Season dimension.
    """
    _execute_ddl(
        connection=connection,
        sql=get_dim_season_ddl(),
        object_name="table 'dim_season'",
    )


def _create_dim_team(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the Team dimension.
    """
    _execute_ddl(
        connection=connection,
        sql=get_dim_team_ddl(),
        object_name="table 'dim_team'",
    )


def _create_dim_player(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the Player dimension.
    """
    _execute_ddl(
        connection=connection,
        sql=get_dim_player_ddl(),
        object_name="table 'dim_player'",
    )


def _create_dim_venue(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the Venue dimension.
    """
    _execute_ddl(
        connection=connection,
        sql=get_dim_venue_ddl(),
        object_name="table 'dim_venue'",
    )


def _create_dim_match(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the Match dimension.
    """
    _execute_ddl(
        connection=connection,
        sql=get_dim_match_ddl(),
        object_name="table 'dim_match'",
    )


def _create_fact_match(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the Match fact table.
    """
    _execute_ddl(
        connection=connection,
        sql=get_fact_match_ddl(),
        object_name="table 'fact_match'",
    )


def _create_fact_player_match(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the Player Match fact table.
    """
    _execute_ddl(
        connection=connection,
        sql=get_fact_player_match_ddl(),
        object_name="table 'fact_player_match'",
    )


def _create_fact_delivery(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the Delivery fact table.
    """
    _execute_ddl(
        connection=connection,
        sql=get_fact_delivery_ddl(),
        object_name="table 'fact_delivery'",
    )


def _create_indexes(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create warehouse indexes.
    """
    logger.info("Creating database indexes.")
    for sql in get_indexes_ddl():
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            connection.commit()
        except Error:
            connection.rollback()
        finally:
            cursor.close()
    logger.info("Database indexes created.")


def create_schema(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Create the complete warehouse schema.
    """
    logger.info("Creating IPL Analytics warehouse schema.")

    _create_database(connection=connection)
    _use_database(connection=connection)

    # Dimensions
    _create_dim_season(connection=connection)
    _create_dim_team(connection=connection)
    _create_dim_player(connection=connection)
    _create_dim_venue(connection=connection)
    _create_dim_match(connection=connection)

    # Facts
    _create_fact_match(connection=connection)
    _create_fact_player_match(connection=connection)
    _create_fact_delivery(connection=connection)

    # Indexes
    _create_indexes(connection=connection)

    logger.info("Warehouse schema created successfully.")


def drop_schema(
    *,
    connection: MySQLConnection,
) -> None:
    """
    Drop the warehouse database.
    """
    logger.warning("Dropping database '%s'.", MYSQL_DATABASE)

    sql = f"DROP DATABASE IF EXISTS `{MYSQL_DATABASE}`;"

    _execute_ddl(
        connection=connection,
        sql=sql,
        object_name=f"database '{MYSQL_DATABASE}'",
    )

    logger.info("Database dropped.")


__all__ = [
    "create_schema",
    "drop_schema",
]