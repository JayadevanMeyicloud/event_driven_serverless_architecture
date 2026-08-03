from app.utils.logger import get_logger

logger = get_logger(__name__)


def generate_daily_report(uploader_name, summary, file_types):

    report = []

    report.append(f"Hello {uploader_name},")
    report.append("")
    report.append("Here is your Daily Upload Report.")
    report.append("")

    report.append(f"Total Files Uploaded : {summary['total_files']}")

    report.append(f"Total Storage Used   : {summary['total_storage']} bytes")

    report.append(f"Successful Uploads   : {summary['success_count']}")

    report.append(f"Failed Uploads       : {summary['failed_count']}")

    report.append("")
    report.append("File Type Summary")
    report.append("---------------------------")

    if file_types:
        for file_type in file_types:
            report.append(f"{file_type['file_type']} : {file_type['count']}")

    else:
        report.append("No files uploaded today.")

    report.append("")
    report.append("Regards,")
    report.append("ABC Cloud Storage Team")

    logger.info("Daily report generated successfully.")

    return "\n".join(report)
