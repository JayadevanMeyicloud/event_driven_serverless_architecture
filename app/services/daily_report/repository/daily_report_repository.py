from app.core.database import get_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Fetch all unique uploaders who uploaded files today.
def get_today_uploaders():

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT DISTINCT
                    uploader_name,
                    uploader_email
                FROM file_metadata
                WHERE uploaded_at >= CURRENT_DATE
                  AND uploaded_at < CURRENT_DATE + INTERVAL '1 day'
                ORDER BY uploader_name;
                """
            )

            rows = cursor.fetchall()

            uploaders = [
                {"uploader_name": row[0], "uploader_email": row[1]} for row in rows
            ]

            logger.info(f"Found {len(uploaders)} uploader(s).")

            return uploaders

    except Exception:
        logger.exception("Failed to fetch today's uploaders.")
        raise

    finally:
        connection.close()


# Fetch all files uploaded today by a specific uploader.
def get_user_upload_summary(uploader_email):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_files,
                    COALESCE(SUM(file_size), 0) AS total_storage,

                    COUNT(*) FILTER
                    (
                        WHERE upload_status = 'SUCCESS'
                    ) AS success_count,

                    COUNT(*) FILTER
                    (
                        WHERE upload_status = 'FAILED'
                    ) AS failed_count

                FROM file_metadata
                WHERE uploader_email = %s
                  AND uploaded_at >= CURRENT_DATE
                  AND uploaded_at < CURRENT_DATE + INTERVAL '1 day';
                """,
                (uploader_email,),
            )

            row = cursor.fetchone()

            summary = {
                "total_files": row[0],
                "total_storage": row[1],
                "success_count": row[2],
                "failed_count": row[3],
            }

            logger.info(f"Summary generated for {uploader_email}")

            return summary

    except Exception:
        logger.exception("Failed to fetch upload summary.")
        raise

    finally:
        connection.close()


# Fetch file type statistics.
def get_file_type_summary(uploader_email):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    file_type,
                    COUNT(*) AS total_files

                FROM file_metadata
                WHERE uploader_email = %s
                  AND uploaded_at >= CURRENT_DATE
                  AND uploaded_at < CURRENT_DATE + INTERVAL '1 day'

                GROUP BY file_type
                ORDER BY total_files DESC;
                """,
                (uploader_email,),
            )

            rows = cursor.fetchall()

            file_types = [{"file_type": row[0], "count": row[1]} for row in rows]

            logger.info(f"Found {len(file_types)} file type(s) for {uploader_email}")

            return file_types

    except Exception:
        logger.exception("Failed to fetch file type summary.")
        raise

    finally:
        connection.close()
