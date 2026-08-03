import json
import boto3

from app.services.metadata.repository.metadata_repository import (
    insert_file_metadata,
)
from app.utils.logger import get_logger
from app.utils.response import (
    success_response,
    error_response,
)

logger = get_logger(__name__)

s3_client = boto3.client("s3")


def lambda_handler(event, context):

    logger.info("Metadata Lambda execution started.")

    try:
        for record in event["Records"]:
            # Read SQS Message
            sqs_message = json.loads(record["body"])

            # Read SNS Message
            sns_message = json.loads(sqs_message["Message"])

            # Process S3 Records
            for s3_record in sns_message["Records"]:
                bucket_name = s3_record["s3"]["bucket"]["name"]
                object_key = s3_record["s3"]["object"]["key"]
                uploaded_at = s3_record["eventTime"]

                logger.info(f"Processing object: {object_key}")

                # Read object metadata from S3
                response = s3_client.head_object(
                    Bucket=bucket_name,
                    Key=object_key,
                )

                object_name = object_key.split("/")[-1]

                file_id = object_name[:36]
                file_name = object_name[37:]

                file_size = response["ContentLength"]
                file_type = response["ContentType"]
                etag = response["ETag"].replace('"', "")

                metadata = response.get("Metadata", {})

                uploader_name = metadata.get(
                    "uploader-name",
                    "",
                )

                uploader_email = metadata.get(
                    "uploader-email",
                    "",
                )

                insert_file_metadata(
                    file_id=file_id,
                    file_name=file_name,
                    file_size=file_size,
                    file_type=file_type,
                    uploader_name=uploader_name,
                    uploader_email=uploader_email,
                    bucket_name=bucket_name,
                    s3_key=object_key,
                    etag=etag,
                    uploaded_at=uploaded_at,
                )

                logger.info(f"Metadata saved successfully for {file_name}")

        logger.info("Metadata Lambda execution completed successfully.")

        return success_response(message="Metadata processed successfully.")

    except Exception:
        logger.exception("Metadata Lambda execution failed.")

        return error_response(
            "Internal Server Error.",
            500,
        )
