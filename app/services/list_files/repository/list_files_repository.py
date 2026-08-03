from math import ceil

from app.core.database import get_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_uploaded_files(uploader_email, page, limit):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # Get total records
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM file_metadata
                WHERE uploader_email = %s;
                """,
                (uploader_email,),
            )

            total_records = cursor.fetchone()[0]

            # Calculate pagination
            offset = (page - 1) * limit
            total_pages = ceil(total_records / limit) if total_records else 0

            # Fetch paginated files
            cursor.execute(
                """
                SELECT
                    id,
                    file_name,
                    file_size,
                    file_type,
                    uploaded_at

                FROM file_metadata

                WHERE uploader_email = %s

                ORDER BY uploaded_at DESC

                LIMIT %s
                OFFSET %s;
                """,
                (uploader_email, limit, offset),
            )

            rows = cursor.fetchall()

            files = [
                {
                    "file_id": str(row[0]),
                    "file_name": row[1],
                    "file_size": row[2],
                    "file_type": row[3],
                    "uploaded_at": row[4].isoformat(),
                }
                for row in rows
            ]

            logger.info(f"Found {len(files)} file(s) for {uploader_email}.")

            return {
                "page": page,
                "limit": limit,
                "total_records": total_records,
                "total_pages": total_pages,
                "files": files,
            }

    except Exception:
        logger.exception("Failed to fetch uploaded files.")
        raise

    finally:
        connection.close()
