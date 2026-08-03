import os
import psycopg
from core.logger import get_logger

logger = get_logger(__name__)


def get_connection():
    try:
        connection = psycopg.connect(
            conninfo=os.environ["DATABASE_URL"],
            sslmode="require"
        )

        logger.info("Database connection established successfully.")

        return connection

    except Exception as e:
        logger.exception(f"Failed to connect to the database: {e}")
        raise