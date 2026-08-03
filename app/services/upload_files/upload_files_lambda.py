import json
import os
import uuid
import boto3

from app.utils.response import (
    success_response,
    error_response,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)

# AWS S3 Client
s3_client = boto3.client("s3")

# Environment Variable
S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]

# Allowed MIME Types
ALLOWED_FILE_TYPES = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/zip",
]


def lambda_handler(event, context):

    logger.info("Upload Files Lambda Started.")

    try:
        # Parse API Gateway Request Body
        body = json.loads(event.get("body", "{}"))

        # Required Fields
        required_fields = [
            "file_name",
            "file_type",
            "uploader_name",
            "uploader_email",
        ]

        missing_fields = [field for field in required_fields if not body.get(field)]

        if missing_fields:
            return error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                400,
            )

        file_name = body["file_name"]
        file_type = body["file_type"]
        uploader_name = body["uploader_name"]
        uploader_email = body["uploader_email"]

        # Validate MIME Type
        if file_type not in ALLOWED_FILE_TYPES:
            return error_response(
                f"{file_type} is not supported.",
                400,
            )

        # Generate UUID
        file_id = str(uuid.uuid4())

        # Generate S3 Object Key
        s3_key = f"uploads/{file_id}-{file_name}"

        # Generate Pre-signed URL
        upload_url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": S3_BUCKET_NAME,
                "Key": s3_key,
                "ContentType": file_type,
                "Metadata": {
                    "uploader-name": uploader_name,
                    "uploader-email": uploader_email,
                },
            },
            ExpiresIn=900,
        )

        logger.info(f"Pre-signed URL generated successfully for {file_name}")

        return success_response(
            data={
                "file_id": file_id,
                "file_name": file_name,
                "file_type": file_type,
                "uploader_name": uploader_name,
                "uploader_email": uploader_email,
                "s3_key": s3_key,
                "upload_url": upload_url,
                "expires_in": 900,
            },
            message="Pre-signed URL generated successfully.",
        )

    except json.JSONDecodeError:
        logger.exception("Invalid JSON body.")

        return error_response(
            "Invalid JSON body.",
            400,
        )

    except Exception:
        logger.exception("Upload Files Lambda Failed.")

        return error_response(
            "Internal Server Error.",
            500,
        )
