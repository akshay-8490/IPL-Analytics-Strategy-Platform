"""
Database connection utilities.

This module provides reusable functions for creating,
testing, and closing MySQL database connections used
throughout the IPL Analytics & Strategy Platform.

Responsibilities
----------------
- Build MySQL connection configuration
- Create database connections
- Validate active connections
- Close database connections safely

This module intentionally contains no SQL logic,
schema creation, or data loading responsibilities.
"""

from __future__ import annotations

import logging
from typing import Any

import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection

from config import (
    MYSQL_AUTOCOMMIT,
    MYSQL_CHARSET,
    MYSQL_CONNECT_TIMEOUT,
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
)

logger = logging.getLogger(__name__)


# ==========================================================
# Private Helpers
# ==========================================================

def _build_connection_config() -> dict[str, Any]:
    """
    Build the MySQL connection configuration.

    Returns
    -------
    dict[str, Any]
        Dictionary of keyword arguments accepted by
        mysql.connector.connect().
    """

    return {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": MYSQL_DATABASE,
        "charset": MYSQL_CHARSET,
        "autocommit": MYSQL_AUTOCOMMIT,
        "connection_timeout": MYSQL_CONNECT_TIMEOUT,
        "use_pure": True,
    }


# ==========================================================
# Public Functions
# ==========================================================

def create_connection() -> MySQLConnection:
    """
    Create a MySQL database connection.

    Returns
    -------
    MySQLConnection
        Active MySQL connection.

    Raises
    ------
    ConnectionError
        If the connection cannot be established.
    """

    logger.info(
        "Creating MySQL connection to database '%s'.",
        MYSQL_DATABASE,
    )

    try:
        config = _build_connection_config()
        try:
            connection = mysql.connector.connect(**config)
        except Error as err:
            # 1049 is the MySQL error code for 'Unknown database'
            if err.errno == 1049:
                logger.warning(
                    "Database '%s' does not exist. Connecting to MySQL server without selecting database.",
                    MYSQL_DATABASE,
                )
                config.pop("database", None)
                connection = mysql.connector.connect(**config)
            else:
                raise

        if not connection.is_connected():
            raise ConnectionError(
                "MySQL connection could not be established."
            )

        logger.info(
            "Successfully connected to MySQL database."
        )

        return connection

    except Error as exc:
        logger.exception(
            "Failed to connect to MySQL database '%s'.",
            MYSQL_DATABASE,
        )
        raise ConnectionError(
            f"Unable to connect to MySQL database '{MYSQL_DATABASE}'."
        ) from exc


def test_connection(
    connection: MySQLConnection,
) -> bool:
    """
    Validate an active MySQL connection.

    Parameters
    ----------
    connection : MySQLConnection
        Active MySQL connection.

    Returns
    -------
    bool
        True if validation succeeds.

    Raises
    ------
    ConnectionError
        If validation fails.
    """

    logger.info("Testing MySQL connection.")

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT 1;")

        cursor.fetchone()

        cursor.close()

        logger.info("Database connection validated successfully.")

        return True

    except Error as exc:
        logger.exception(
            "Database connection validation failed."
        )

        raise ConnectionError(
            "Failed to validate MySQL connection."
        ) from exc


def close_connection(
    connection: MySQLConnection | None,
) -> None:
    """
    Close a MySQL connection safely.

    Parameters
    ----------
    connection : MySQLConnection | None
        Active database connection.

    Returns
    -------
    None
    """

    if connection is None:
        return

    try:
        if connection.is_connected():

            logger.info("Closing MySQL connection.")

            connection.close()

            logger.info("Database connection closed.")

    except Error:
        logger.exception(
            "An error occurred while closing the database connection."
        )


__all__ = [
    "create_connection",
    "test_connection",
    "close_connection",
]