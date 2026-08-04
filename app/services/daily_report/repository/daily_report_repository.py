from app.core.database import get_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_daily_report(
    uploader_email=None,
    page=1,
    limit=100,
):

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            # Call Stored Procedure
            cursor.execute(
                """
                CALL get_daily_report(
                    %s,
                    %s,
                    %s,
                    'uploaders',
                    'summary',
                    'filetypes'
                );
                """,
                (uploader_email, page, limit),
            )

            # fetch uploaders if uploader_email is None
            if uploader_email is None:
                cursor.execute("FETCH ALL FROM uploaders;")

                rows = cursor.fetchall()

                uploaders = [
                    {
                        "uploader_name": row[0],
                        "uploader_email": row[1],
                    }
                    for row in rows
                ]

                connection.commit()

                logger.info(f"Fetched {len(uploaders)} uploader(s).")

                return uploaders

            # fetch summary and file type statistics if uploader_email is provided
            else:
                # Fetch Summary
                cursor.execute("FETCH ALL FROM summary;")

                row = cursor.fetchone()

                summary = {
                    "total_files": row[0],
                    "total_storage": row[1],
                    "success_count": row[2],
                    "failed_count": row[3],
                }

                # Fetch File Type Summary
                cursor.execute("FETCH ALL FROM filetypes;")

                rows = cursor.fetchall()

                file_types = [
                    {
                        "file_type": row[0],
                        "count": row[1],
                    }
                    for row in rows
                ]

                connection.commit()

                logger.info(f"Fetched report for {uploader_email}")

                return {
                    "summary": summary,
                    "file_types": file_types,
                }

    except Exception:
        connection.rollback()

        logger.exception("Failed to fetch daily report.")

        raise

    finally:
        connection.close()


