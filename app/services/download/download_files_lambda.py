import boto3

from app.utils.logger import get_logger
from app.utils.response import success_response, error_response
from app.services.download.repository.download_repository import get_file_by_id

logger = get_logger(__name__)

s3_client = boto3.client("s3")


def lambda_handler(event, context):

    logger.info("Download Lambda Started.")

    try:
        # Read Query Parameters
        query_params = event.get("queryStringParameters") or {}

        file_id = query_params.get("file_id")

        # Validate file_id
        if not file_id:
            return error_response("file_id is required.", 400)

        logger.info(f"Fetching file details for file_id: {file_id}")

        # Fetch file details from DB
        file_details = get_file_by_id(file_id)

        if not file_details:
            return error_response("File not found.", 404)

        bucket_name = file_details["bucket_name"]
        s3_key = file_details["s3_key"]

        # Verify object exists in S3
        s3_client.head_object(Bucket=bucket_name, Key=s3_key)

        # Generate Download URL
        download_url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket_name, "Key": s3_key},
            ExpiresIn=900,
        )

        logger.info(f"Download URL generated for {file_id}")

        return success_response(
            data={"download_url": download_url},
            message="Download URL generated successfully.",
        )

    except s3_client.exceptions.NoSuchKey:
        logger.exception("File not found in S3.")

        return error_response("File not found in storage.", 404)

    except Exception:
        logger.exception("Download Lambda Failed.")

        return error_response("Internal Server Error.", 500)
