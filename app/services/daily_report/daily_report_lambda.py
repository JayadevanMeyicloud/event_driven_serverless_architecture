from app.services.daily_report.repository.daily_report_repository import (
    get_today_uploaders,
    get_user_upload_summary,
    get_file_type_summary,
)

from app.services.daily_report.service.report_service import generate_daily_report
from app.services.daily_report.service.email_service import send_email

from app.utils.logger import get_logger
from app.utils.response import (
    success_response,
    error_response,
)

logger = get_logger(__name__)


def lambda_handler(event, context):

    logger.info("Daily Report Lambda Started")

    try:
        # Fetch all uploaders who uploaded files today
        uploaders = get_today_uploaders()

        logger.info(f"Today's Uploaders: {uploaders}")

        # No uploads today
        if not uploaders:
            logger.info("No uploads found for today.")

            return success_response(message="No uploads found for today.")

        # Generate report for each uploader
        for uploader in uploaders:
            uploader_name = uploader["uploader_name"]
            uploader_email = uploader["uploader_email"]

            logger.info(f"Generating report for {uploader_name} ({uploader_email})")

            # Fetch upload summary
            summary = get_user_upload_summary(uploader_email)

            # Fetch file type statistics
            file_types = get_file_type_summary(uploader_email)

            # Generate report
            report = generate_daily_report(uploader_name, summary, file_types)

            logger.info(report)

            # Send email
            send_email(
                recipient_email=uploader_email,
                subject="Daily Upload Report",
                body=report,
            )

        return success_response(message="Daily report generated successfully.")

    except ValueError as e:
        logger.exception(str(e))

        return error_response(str(e), 400)

    except Exception:
        logger.exception("Daily Report Lambda Failed")

        return error_response("Internal Server Error", 500)
