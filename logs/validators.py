import ipaddress
import math
from datetime import datetime

from django.core.exceptions import ValidationError


VALID_SEVERITIES = {
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def validate_log_data(data):
    """
    Validate raw log data before it is saved
    to the database.

    Returns:
        (True, None) if valid
        (False, error_message) if invalid
    """

    errors = []

    # -----------------------------------------
    # Timestamp
    # -----------------------------------------

    timestamp = data.get("timestamp")

    if not timestamp:
        errors.append("Missing timestamp")

    elif isinstance(timestamp, str):

        try:
            datetime.strptime(
                timestamp.strip(),
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:
            errors.append(
                "Invalid timestamp format. "
                "Expected YYYY-MM-DD HH:MM:SS"
            )

    # -----------------------------------------
    # IP address
    # -----------------------------------------

    ip_address = data.get("ip_address")

    if not ip_address:

        errors.append(
            "Missing IP address"
        )

    else:

        try:
            ipaddress.ip_address(
                str(ip_address).strip()
            )

        except ValueError:

            errors.append(
                "Invalid IP address"
            )

    # -----------------------------------------
    # Event type
    # -----------------------------------------

    event_type = data.get("event_type")

    if not event_type or not str(event_type).strip():

        errors.append(
            "Missing event type"
        )

    # -----------------------------------------
    # Severity
    # -----------------------------------------

    severity = data.get("severity")

    if not severity:

        errors.append(
            "Missing severity"
        )

    elif str(severity).upper() not in VALID_SEVERITIES:

        errors.append(
            f"Invalid severity: {severity}"
        )

    # -----------------------------------------
    # HTTP status code
    # -----------------------------------------

    status_code = data.get("status_code")

    if status_code in (None, ""):

        errors.append(
            "Missing HTTP status code"
        )

    else:

        try:

            status_code = int(status_code)

            if not 100 <= status_code <= 599:

                errors.append(
                    "HTTP status code must "
                    "be between 100 and 599"
                )

        except (ValueError, TypeError):

            errors.append(
                "HTTP status code must be an integer"
            )

    # -----------------------------------------
    # Response time
    # -----------------------------------------

    response_time = data.get("response_time")

    if response_time in (None, ""):

        errors.append(
            "Missing response time"
        )

    else:

        try:

            response_time = float(
                response_time
            )

            if response_time < 0:

                errors.append(
                    "Response time cannot be negative"
                )

            elif not math.isfinite(
                response_time
            ):

                errors.append(
                    "Response time must be finite"
                )

        except (ValueError, TypeError):

            errors.append(
                "Response time must be a number"
            )

    # -----------------------------------------
    # Message
    # -----------------------------------------

    message = data.get("message")

    if not message or not str(message).strip():

        errors.append(
            "Missing message"
        )

    # -----------------------------------------
    # Final result
    # -----------------------------------------

    if errors:

        return False, errors

    return True, None