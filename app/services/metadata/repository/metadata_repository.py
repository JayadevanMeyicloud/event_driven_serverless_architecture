import uuid

from app.core.database import get_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)


def insert_file_metadata(
    file_id,
    file_name,
    file_size,
    file_type,
    uploader_name,
    uploader_email,
    bucket_name,
    s3_key,
    etag,
    uploaded_at,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO file_metadata
                (
                    id,
                    file_name,
                    file_size,
                    file_type,
                    uploader_name,
                    uploader_email,
                    bucket_name,
                    s3_key,
                    etag,
                    upload_status,
                    uploaded_at
                )
                VALUES
                (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (s3_key)
                DO NOTHING
                """,
                (
                    file_id,
                    file_name,
                    file_size,
                    file_type,
                    uploader_name,
                    uploader_email,
                    bucket_name,
                    s3_key,
                    etag,
                    "SUCCESS",
                    uploaded_at,
                ),
            )

            connection.commit()

            logger.info("File metadata inserted successfully.")

    except Exception:
        logger.exception("Failed to insert file metadata.")
        raise

    finally:
        connection.close()
