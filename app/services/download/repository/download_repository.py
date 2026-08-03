from app.core.database import get_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Fetch file details using file_id.
def get_file_by_id(file_id):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    bucket_name,
                    s3_key,
                    file_name,
                    file_type

                FROM file_metadata

                WHERE id = %s;
                """,
                (file_id,),
            )

            row = cursor.fetchone()

            if not row:
                return None

            file_details = {
                "file_id": row[0],
                "bucket_name": row[1],
                "s3_key": row[2],
                "file_name": row[3],
                "file_type": row[4],
            }

            logger.info(f"File found for file_id: {file_id}")

            return file_details

    except Exception:
        logger.exception("Failed to fetch file details.")
        raise

    finally:
        connection.close()
