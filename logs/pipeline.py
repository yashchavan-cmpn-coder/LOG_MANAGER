from .anamoly import detect_anomalies
from .ai_service import explain_anomaly
from .models import Anomaly


def run_analysis_pipeline(ai_limit=5):
    """
    Run anomaly detection and optionally generate
    AI explanations for a limited number of anomalies.

    ai_limit prevents excessive API calls in a
    single execution.
    """

    # ---------------------------------------------
    # Step 1: Detect anomalies
    # ---------------------------------------------

    detection_result = detect_anomalies()

    # ---------------------------------------------
    # Step 2: Find anomalies that still need AI
    # ---------------------------------------------

    pending_anomalies = (
        Anomaly.objects
        .select_related("log")
        .filter(
            ai_explanation=""
        )
        .order_by("detected_at")[:ai_limit]
    )

    ai_generated = 0
    ai_failed = 0

    # ---------------------------------------------
    # Step 3: Generate limited AI analyses
    # ---------------------------------------------

    for anomaly in pending_anomalies:

        result = explain_anomaly(anomaly)

        if "error" in result:

            ai_failed += 1

        else:

            ai_generated += 1

    # ---------------------------------------------
    # Step 4: Count remaining pending analyses
    # ---------------------------------------------

    remaining_ai = Anomaly.objects.filter(
        ai_explanation=""
    ).count()

    # ---------------------------------------------
    # Step 5: Return summary
    # ---------------------------------------------

    return {
        "detection": detection_result,
        "ai_generated": ai_generated,
        "ai_failed": ai_failed,
        "remaining_ai": remaining_ai,
        "total_anomalies": Anomaly.objects.count(),
    }