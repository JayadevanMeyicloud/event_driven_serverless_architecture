import boto3
import os

print("EMAIL SERVICE LOADED")
print(os)

from app.utils.logger import get_logger

logger = get_logger(__name__)

ses_client = boto3.client("ses")
SOURCE_EMAIL = os.environ["SES_SOURCE_EMAIL"]


def send_upload_notification(
    uploader_name, uploader_email, file_name, file_size, file_type
):
    # Sends an upload success email using Amazon SES.

    subject = "File Uploaded Successfully"

    body = f"""
Hello {uploader_name},

Your file has been uploaded successfully.

File Details
------------------------
File Name : {file_name}
File Type : {file_type}
File Size : {file_size} bytes

Thank you for using File Storage System.

Regards,
File Storage Team
"""

    response = ses_client.send_email(
        Source=SOURCE_EMAIL,
        Destination={"ToAddresses": [uploader_email]},
        Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
    )

    logger.info(
        f"Email sent successfully to {uploader_email}. "
        f"Message ID: {response['MessageId']}"
    )
