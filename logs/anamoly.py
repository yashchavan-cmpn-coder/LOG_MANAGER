import numpy as np
from django.db import transaction

from .models import LogEntry, Anomaly


SEVERITY_SCORES = {
    "INFO": 0,
    "WARNING": 1,
    "ERROR": 3,
    "CRITICAL": 5,
}


VALID_SEVERITIES = {
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def calculate_z_score(value, mean, std):
    """
    Calculate how far a value is from the mean.
    """

    if std == 0:
        return 0

    return (value - mean) / std


def detect_anomalies():
    """
    Analyze all valid logs and flag unusual entries.

    The anomaly decision is made entirely by this
    algorithm. AI is not involved in detection.
    """

    logs = list(
        LogEntry.objects.all()
    )

    # --------------------------------------------------
    # Edge Case 1: Empty dataset
    # --------------------------------------------------

    if not logs:

        return {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "anomalies": 0,
            "message": "No logs available for analysis.",
        }

    # --------------------------------------------------
    # Validate logs before statistical analysis
    # --------------------------------------------------

    valid_logs = []
    invalid_count = 0

    for log in logs:

        try:

            # Timestamp validation
            if log.timestamp is None:
                raise ValueError(
                    "Missing timestamp"
                )

            # Severity validation
            if not log.severity:
                raise ValueError(
                    "Missing severity"
                )

            severity = log.severity.upper()

            if severity not in VALID_SEVERITIES:
                raise ValueError(
                    f"Invalid severity: {log.severity}"
                )

            # Status code validation
            if log.status_code is None:
                raise ValueError(
                    "Missing HTTP status code"
                )

            if not (
                100 <= int(log.status_code) <= 599
            ):
                raise ValueError(
                    f"Invalid HTTP status code: "
                    f"{log.status_code}"
                )

            # Response-time validation
            if log.response_time is None:
                raise ValueError(
                    "Missing response time"
                )

            response_time = float(
                log.response_time
            )

            if response_time < 0:
                raise ValueError(
                    "Negative response time"
                )

            if not np.isfinite(response_time):
                raise ValueError(
                    "Invalid response time"
                )

            valid_logs.append(log)

        except (
            ValueError,
            TypeError,
        ):

            invalid_count += 1

            # Make sure invalid data is never
            # accidentally treated as an anomaly.
            if log.is_anomaly:

                log.is_anomaly = False

                log.save(
                    update_fields=["is_anomaly"]
                )

    # --------------------------------------------------
    # Edge Case 2: No valid logs
    # --------------------------------------------------

    if not valid_logs:

        return {
            "total": len(logs),
            "valid": 0,
            "invalid": invalid_count,
            "anomalies": 0,
            "message": "No valid logs available for analysis.",
        }

    # --------------------------------------------------
    # Calculate response-time statistics
    # ONLY using valid logs
    # --------------------------------------------------

    response_times = np.array(
        [
            float(log.response_time)
            for log in valid_logs
        ],
        dtype=float
    )

    mean_response_time = np.mean(
        response_times
    )

    std_response_time = np.std(
        response_times
    )

    anomaly_count = 0

    # --------------------------------------------------
    # Analyze every valid log
    # --------------------------------------------------

    for log in valid_logs:

        score = 0
        reasons = []

        severity = log.severity.upper()

        # ----------------------------------------------
        # 1. Severity score
        # ----------------------------------------------

        severity_score = SEVERITY_SCORES.get(
            severity,
            0
        )

        score += severity_score

        if severity_score >= 3:

            reasons.append(
                f"High severity level: {severity}"
            )

        # ----------------------------------------------
        # 2. HTTP status score
        # ----------------------------------------------

        status_code = int(
            log.status_code
        )

        if 500 <= status_code <= 599:

            score += 4

            reasons.append(
                f"Server error HTTP {status_code}"
            )

        elif 400 <= status_code <= 499:

            score += 2

            reasons.append(
                f"Client error HTTP {status_code}"
            )

        # ----------------------------------------------
        # 3. Response-time anomaly
        # ----------------------------------------------

        z_score = calculate_z_score(
            float(log.response_time),
            mean_response_time,
            std_response_time
        )

        if abs(z_score) >= 3:

            score += 4

            reasons.append(
                f"Abnormally high response time "
                f"({float(log.response_time):.2f} ms)"
            )

        # ----------------------------------------------
        # Final decision
        # ----------------------------------------------

        is_anomaly = score >= 5

        log.is_anomaly = is_anomaly

        log.save(
            update_fields=["is_anomaly"]
        )

        if is_anomaly:

            anomaly_count += 1

            reason = "; ".join(reasons)

            # Safety fallback
            if not reason:

                reason = (
                    "Anomaly score exceeded "
                    "the configured threshold."
                )

            with transaction.atomic():

                Anomaly.objects.update_or_create(
                    log=log,
                    defaults={
                        "score": score,
                        "reason": reason,
                    }
                )

        else:

            # Remove stale anomaly records
            # if a previously anomalous log
            # is now considered normal.
            Anomaly.objects.filter(
                log=log
            ).delete()

    return {
        "total": len(logs),
        "valid": len(valid_logs),
        "invalid": invalid_count,
        "anomalies": anomaly_count,
        "message": "Anomaly detection completed successfully.",
    }