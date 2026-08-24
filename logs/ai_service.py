import os
import json

from dotenv import load_dotenv
from google import genai

from .models import Anomaly


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def explain_anomaly(anomaly):
    """
    Send an already-detected anomaly to Gemini
    and generate an explanation, root cause,
    and recommended next step.
    """

    log = anomaly.log

    prompt = f"""
You are a system log analysis assistant.

The application has ALREADY detected this log as anomalous
using its own anomaly detection algorithm.

You must NOT decide whether the log is anomalous.

Your task is only to explain the already-detected anomaly.

Analyze the following information:

Timestamp: {log.timestamp}
IP Address: {log.ip_address}
Event Type: {log.event_type}
Severity: {log.severity}
HTTP Status: {log.status_code}
Response Time: {log.response_time} ms
Message: {log.message}

Anomaly Score: {anomaly.score}

Detection Reason:
{anomaly.reason}

Return your response in exactly this JSON format:

{{
    "explanation": "A simple plain-English explanation of what happened.",
    "root_cause": "The most likely root cause. Clearly mention uncertainty if the exact cause cannot be determined.",
    "recommended_action": "The most useful next step for investigating or resolving the issue."
}}

Do not invent information that is not present in the log.
"""


    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        response_text = response.text.strip()

        # Remove markdown code fences if Gemini adds them
        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "")
            response_text = response_text.replace("```", "")
            response_text = response_text.strip()

        result = json.loads(response_text)

        anomaly.ai_explanation = result.get(
            "explanation",
            ""
        )

        anomaly.root_cause = result.get(
            "root_cause",
            ""
        )

        anomaly.recommended_action = result.get(
            "recommended_action",
            ""
        )

        anomaly.save(
            update_fields=[
                "ai_explanation",
                "root_cause",
                "recommended_action",
            ]
        )

        return result

    except Exception as e:

        return {
            "error": str(e)
        }