from typing import Optional

import asyncpg
from loguru import logger

from .config import db_config

_pool: Optional[asyncpg.Pool] = None


async def init_db_pool() -> None:
    """
    Initialize the PostgreSQL connection pool and create the products table if it doesn't exist.

    This function is meant to be called at the startup of the FastAPI app to
    initialize a connection pool to PostgreSQL and ensure that the required
    database schema is in place.
    """
    global _pool
    try:
        _pool = await asyncpg.create_pool(
            dsn=db_config.dsn,
            min_size=db_config.pool_min_size,
            max_size=db_config.pool_max_size,
        )
        logger.info("PostgreSQL connection pool created successfully.")

    except Exception as e:
        logger.error(f"Error initializing PostgreSQL connection pool: {e}")
        raise


async def get_db_pool() -> asyncpg.Pool:
    """
    Return the PostgreSQL connection pool.

    This function returns the connection pool object, from which individual
    connections can be acquired as needed for database operations. The caller
    is responsible for acquiring and releasing connections from the pool.

    Returns
    -------
    asyncpg.Pool
        The connection pool object to the PostgreSQL database.

    Raises
    ------
    ConnectionError
        Raised if the connection pool is not initialized.
    """
    global _pool
    if _pool is None:
        logger.error("Connection pool is not initialized.")
        raise ConnectionError("PostgreSQL connection pool is not initialized.")
    try:
        return _pool
    except Exception as e:
        logger.error(f"Failed to return PostgreSQL connection pool: {e}")
        raise


async def close_db_pool() -> None:
    """
    Close the PostgreSQL connection pool.

    This function should be called during the shutdown of the FastAPI app
    to properly close all connections in the pool and release resources.
    """
    global _pool
    if _pool is not None:
        try:
            logger.info("Closing PostgreSQL connection pool...")
            await _pool.close()
            logger.info("PostgreSQL connection pool closed successfully.")
        except Exception as e:
            logger.error(f"Error closing PostgreSQL connection pool: {e}")
            raise
    else:
        logger.warning("PostgreSQL connection pool was not initialized.")
