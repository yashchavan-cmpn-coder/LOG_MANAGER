from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404

from .models import LogEntry, Anomaly


def dashboard(request):
    logs = LogEntry.objects.all().order_by("-timestamp")

    context = {
        "logs": logs,
        "total_logs": LogEntry.objects.count(),
        "total_anomalies": Anomaly.objects.count(),
        "normal_logs": LogEntry.objects.filter(
            is_anomaly=False
        ).count(),
    }

    return render(
        request,
        "logs/dashboard.html",
        context
    )


def anomaly_detail(request, anomaly_id):
    anomaly = get_object_or_404(
        Anomaly.objects.select_related("log"),
        id=anomaly_id
    )

    return render(
        request,
        "logs/anomaly_detail.html",
        {
            "anomaly": anomaly
        }
    )


from django.shortcuts import redirect
from .ai_service import explain_anomaly


def generate_ai_analysis(request, anomaly_id):

    anomaly = get_object_or_404(
        Anomaly.objects.select_related("log"),
        id=anomaly_id
    )

    # Generate AI analysis only when user requests it
    explain_anomaly(anomaly)

    return redirect(
        "logs:anomaly_detail",
        anomaly_id=anomaly.id
    )

import csv
import io

from django.contrib import messages
from django.shortcuts import redirect
from django.db import transaction

from .models import LogEntry

import csv
import io

from django.contrib import messages
from django.shortcuts import redirect
from django.db import transaction

from .models import LogEntry, Anomaly


def detect_anomaly(log):
    """
    Analyze a LogEntry and return:
    (is_anomaly, score, reason)
    """

    score = 0
    reasons = []

    # -----------------------------
    # Severity
    # -----------------------------

    if log.severity == "CRITICAL":
        score += 50
        reasons.append("Critical severity detected.")

    elif log.severity == "ERROR":
        score += 35
        reasons.append("Error-level event detected.")

    elif log.severity == "WARNING":
        score += 15
        reasons.append("Warning-level event detected.")

    # -----------------------------
    # HTTP status
    # -----------------------------

    if log.status_code >= 500:
        score += 40
        reasons.append(
            f"Server error HTTP status {log.status_code} detected."
        )

    elif log.status_code == 401:
        score += 25
        reasons.append(
            "Unauthorized request detected."
        )

    elif log.status_code == 403:
        score += 25
        reasons.append(
            "Forbidden request detected."
        )

    elif log.status_code == 404:
        score += 10
        reasons.append(
            "Resource-not-found response detected."
        )

    # -----------------------------
    # Response time
    # -----------------------------

    if log.response_time >= 5000:
        score += 40
        reasons.append(
            "Extremely high response time detected."
        )

    elif log.response_time >= 2000:
        score += 30
        reasons.append(
            "Very high response time detected."
        )

    elif log.response_time >= 1000:
        score += 20
        reasons.append(
            "High response time detected."
        )

    # -----------------------------
    # Message analysis
    # -----------------------------

    message = log.message.lower()

    suspicious_keywords = {
        "failed": 15,
        "failure": 15,
        "timeout": 20,
        "unavailable": 25,
        "attack": 30,
        "unauthorized": 25,
        "database connection failed": 30,
        "server unavailable": 30,
    }

    for keyword, points in suspicious_keywords.items():

        if keyword in message:

            score += points

            reasons.append(
                f"Suspicious message pattern: '{keyword}'."
            )

    # -----------------------------
    # Maximum score
    # -----------------------------

    score = min(score, 100)

    # -----------------------------
    # Anomaly threshold
    # -----------------------------

    is_anomaly = score >= 40

    reason = " ".join(reasons)

    if not reason:
        reason = "No significant abnormal behavior detected."

    return is_anomaly, score, reason


def upload_csv(request):

    if request.method != "POST":
        return redirect("logs:dashboard")

    # --------------------------------
    # Check file
    # --------------------------------

    if "csv_file" not in request.FILES:

        messages.error(
            request,
            "Please select a CSV file."
        )

        return redirect("logs:dashboard")

    uploaded_file = request.FILES["csv_file"]

    if not uploaded_file.name.lower().endswith(".csv"):

        messages.error(
            request,
            "Only CSV files are allowed."
        )

        return redirect("logs:dashboard")

    if uploaded_file.size == 0:

        messages.error(
            request,
            "The uploaded CSV file is empty."
        )

        return redirect("logs:dashboard")

    existing_logs = LogEntry.objects.count()

    try:

        # --------------------------------
        # Read CSV
        # --------------------------------

        decoded_file = uploaded_file.read().decode("utf-8-sig")

        csv_file = io.StringIO(decoded_file)

        reader = csv.DictReader(csv_file)

        # --------------------------------
        # Required columns
        # --------------------------------

        required_columns = {
            "timestamp",
            "ip_address",
            "event_type",
            "severity",
            "status_code",
            "response_time",
            "message",
        }

        if not reader.fieldnames:

            messages.error(
                request,
                "CSV file does not contain any columns."
            )

            return redirect("logs:dashboard")

        reader.fieldnames = [
            field.strip()
            for field in reader.fieldnames
        ]

        missing_columns = (
            required_columns
            - set(reader.fieldnames)
        )

        if missing_columns:

            messages.error(
                request,
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

            return redirect("logs:dashboard")

        # --------------------------------
        # Import records
        # --------------------------------

        imported_count = 0
        skipped_count = 0
        anomaly_count = 0

        with transaction.atomic():

            for row in reader:

                # Skip empty rows

                if not any(
                    value and value.strip()
                    for value in row.values()
                    if value is not None
                ):

                    skipped_count += 1
                    continue

                # --------------------------------
                # Create Log
                # --------------------------------

                log = LogEntry.objects.create(

                    timestamp=row["timestamp"].strip(),

                    ip_address=row["ip_address"].strip(),

                    event_type=row["event_type"].strip(),

                    severity=row["severity"].strip().upper(),

                    status_code=int(
                        row["status_code"].strip()
                    ),

                    response_time=float(
                        row["response_time"].strip()
                    ),

                    message=row["message"].strip(),

                )

                imported_count += 1

                # --------------------------------
                # Detect anomaly
                # --------------------------------

                is_anomaly, score, reason = detect_anomaly(log)

                if is_anomaly:

                    log.is_anomaly = True
                    log.save(update_fields=["is_anomaly"])

                    Anomaly.objects.create(

                        log=log,

                        score=score,

                        reason=reason,

                    )

                    anomaly_count += 1

        # --------------------------------
        # Final counts
        # --------------------------------

        total_logs = LogEntry.objects.count()

        total_anomalies = Anomaly.objects.count()

        # --------------------------------
        # Success message
        # --------------------------------

        messages.success(
            request,

            f"CSV imported successfully! "
            f"Existing logs: {existing_logs} | "
            f"Imported: {imported_count} | "
            f"Skipped: {skipped_count} | "
            f"New anomalies: {anomaly_count} | "
            f"Total logs: {total_logs} | "
            f"Total anomalies: {total_anomalies}"
        )

        return redirect("logs:dashboard")

    except UnicodeDecodeError:

        messages.error(
            request,
            "The CSV file must use UTF-8 encoding."
        )

        return redirect("logs:dashboard")

    except ValueError as e:

        messages.error(
            request,
            f"Invalid data in CSV file: {str(e)}"
        )

        return redirect("logs:dashboard")

    except Exception as e:

        messages.error(
            request,
            f"Unable to import CSV file: {str(e)}"
        )

        return redirect("logs:dashboard")