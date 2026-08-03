import json
import boto3

from app.utils.logger import get_logger
from app.utils.response import success_response, error_response
from app.services.audit_logs.repository.audit_log_repository import save_audit_log

logger = get_logger(__name__)

s3_client = boto3.client("s3")


def lambda_handler(event, context):

    logger.info("Audit Lambda triggered")

    try:
        for record in event["Records"]:
            # Read SQS Message
            sqs_body = json.loads(record["body"])

            # Read SNS Message
            sns_message = json.loads(sqs_body["Message"])

            # Process S3 Records
            for s3_record in sns_message["Records"]:
                bucket_name = s3_record["s3"]["bucket"]["name"]
                s3_key = s3_record["s3"]["object"]["key"]
                event_time = s3_record["eventTime"]

                logger.info(f"Processing object: {s3_key}")

                object_name = s3_key.split("/")[-1]
                file_id = object_name[:36]

                # Read uploader metadata
                response = s3_client.head_object(Bucket=bucket_name, Key=s3_key)

                metadata = response.get("Metadata", {})

                uploader_email = metadata.get("uploader-email", "unknown")

                save_audit_log(
                    file_id=file_id,
                    uploader_email=uploader_email,
                    event_type="FILE_UPLOAD",
                    status="SUCCESS",
                    error_message=None,
                    event_time=event_time,
                )

                logger.info(f"Audit log saved successfully for {uploader_email}")

        return success_response(message="Audit logs processed successfully.")

    except ValueError as e:
        logger.exception(str(e))

        return error_response(str(e), 400)

    except Exception:
        logger.exception("Audit Lambda execution failed.")

        return error_response("Internal Server Error", 500)
