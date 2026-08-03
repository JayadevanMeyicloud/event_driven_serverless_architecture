import uuid

from app.core.database import get_connection
from app.utils.logger import get_logger

logger = get_logger(__name__)


def save_audit_log(file_id, uploader_email, event_type, status, error_message, event_time):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO audit_logs
            (id, file_id, uploader_email, event_type, status, error_message, event_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                str(uuid.uuid4()),
                file_id,
                uploader_email,
                event_type,
                status,
                error_message,
                event_time,
            ),
        )

        conn.commit()
        logger.info(f"Audit log saved - {event_type} {status}")

    except Exception as e:
        logger.error(f"DB insert failed: {str(e)}")
        raise

    finally:
        cursor.close()
        conn.close()