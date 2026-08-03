import json

from app.utils.logger import get_logger
from app.utils.response import success_response, error_response
from app.services.list_files.repository.list_files_repository import get_uploaded_files

logger = get_logger(__name__)


def lambda_handler(event, context):

    logger.info("List Files Lambda Started.")

    try:
        # Read Query Parameters
        query_params = event.get("queryStringParameters") or {}

        uploader_email = query_params.get("uploader_email")
        page = int(query_params.get("page", 1))
        limit = int(query_params.get("limit", 10))

        # Validate uploader email
        if not uploader_email:
            return error_response("uploader_email is required.", 400)

        # Validate page
        if page < 1:
            return error_response("page must be greater than or equal to 1.", 400)

        # Validate limit
        if limit < 1 or limit > 100:
            return error_response("limit must be between 1 and 100.", 400)

        logger.info(f"Fetching files for {uploader_email} | Page={page}, Limit={limit}")

        response = get_uploaded_files(
            uploader_email=uploader_email, page=page, limit=limit
        )

        logger.info(f"Successfully fetched {len(response['files'])} file(s).")

        return success_response(data=response, message="Files fetched successfully.")

    except ValueError:
        logger.exception("Invalid page or limit.")

        return error_response("page and limit must be valid integers.", 400)

    except Exception:
        logger.exception("List Files Lambda Failed.")

        return error_response("Internal Server Error.", 500)
