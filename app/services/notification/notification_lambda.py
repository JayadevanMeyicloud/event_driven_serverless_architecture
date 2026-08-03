import json
import boto3

from app.services.notification.service.email_service import (
    send_upload_notification,
)
from app.utils.logger import get_logger
from app.utils.response import (
    success_response,
    error_response,
)

logger = get_logger(__name__)

s3_client = boto3.client("s3")


def lambda_handler(event, context):

    logger.info("Notification Lambda started.")

    try:
        for record in event["Records"]:
            # Read SQS Message
            sns_message = json.loads(record["body"])

            logger.info("SQS Message:")
            logger.info(json.dumps(sns_message, indent=2))

            # Read SNS Message
            s3_event = json.loads(sns_message["Message"])

            logger.info("S3 Event:")
            logger.info(json.dumps(s3_event, indent=2))

            # Validate S3 Event
            if "Records" not in s3_event:
                logger.warning("Invalid S3 event received. Skipping message.")

                logger.warning(json.dumps(s3_event, indent=2))

                continue

            # Read S3 Record
            s3_record = s3_event["Records"][0]

            bucket_name = s3_record["s3"]["bucket"]["name"]
            object_key = s3_record["s3"]["object"]["key"]

            logger.info(f"Bucket : {bucket_name}")
            logger.info(f"Object : {object_key}")

            # Read S3 Object Metadata
            response = s3_client.head_object(
                Bucket=bucket_name,
                Key=object_key,
            )

            metadata = response.get("Metadata", {})

            uploader_name = metadata.get(
                "uploader-name",
                "",
            )

            uploader_email = metadata.get(
                "uploader-email",
                "",
            )

            file_name = object_key.split("/")[-1]
            file_size = response["ContentLength"]
            file_type = response["ContentType"]

            # Send Email Notification
            send_upload_notification(
                uploader_name=uploader_name,
                uploader_email=uploader_email,
                file_name=file_name,
                file_size=file_size,
                file_type=file_type,
            )

            logger.info(f"Notification email sent successfully to {uploader_email}")

        return success_response(message="Notification processed successfully.")

    except Exception:
        logger.exception("Notification Lambda failed.")

        return error_response(
            "Internal Server Error.",
            500,
        )
