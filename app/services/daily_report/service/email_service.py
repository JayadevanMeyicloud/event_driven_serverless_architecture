import os
import boto3

from app.utils.logger import get_logger

logger = get_logger(__name__)

ses_client = boto3.client("ses")
SENDER_EMAIL = os.environ["SENDER_EMAIL"]


# Send a plain text email using Amazon SES.
def send_email(recipient_email, subject, body):

    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={"ToAddresses": [recipient_email]},
            Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
        )

        logger.info(f"Email sent successfully to {recipient_email}")

        return response

    except Exception:
        logger.exception(f"Failed to send email to {recipient_email}")
        raise