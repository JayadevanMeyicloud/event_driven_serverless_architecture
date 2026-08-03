import json


def success_response(data=None, message="Success", status_code=200):
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "success": True,
            "message": message,
            "data": data
        })
    }


def error_response(message, status_code=400):
    return {
        "statusCode": status_code,
        "body": json.dumps({
            "success": False,
            "message": message
        })
    }