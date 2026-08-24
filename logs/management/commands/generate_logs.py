import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from logs.models import LogEntry


class Command(BaseCommand):
    help = "Generate sample log data with injected anomalies"

    def handle(self, *args, **options):

        # Clear existing logs
        LogEntry.objects.all().delete()

        ips = [
            "192.168.1.10",
            "192.168.1.20",
            "192.168.1.30",
            "10.0.0.15",
            "10.0.0.25",
            "203.0.113.7",
        ]

        events = [
            "GET /api/users",
            "GET /api/products",
            "GET /api/orders",
            "POST /api/login",
            "POST /api/payment",
            "GET /api/profile",
            "GET /admin",
        ]

        normal_messages = [
            "Request successful",
            "Request completed successfully",
            "Resource retrieved",
            "User authenticated successfully",
        ]

        now = timezone.now()

        logs = []

        # Generate normal logs
        for i in range(450):

            timestamp = now - timedelta(
                minutes=random.randint(0, 1440)
            )

            ip = random.choice(ips)
            event = random.choice(events)

            severity = random.choices(
                ["INFO", "WARNING", "ERROR"],
                weights=[80, 15, 5]
            )[0]

            if severity == "INFO":
                status_code = 200
                response_time = random.uniform(80, 300)

            elif severity == "WARNING":
                status_code = random.choice([400, 404])
                response_time = random.uniform(200, 500)

            else:
                status_code = random.choice([500, 502, 503])
                response_time = random.uniform(300, 800)

            logs.append(
                LogEntry(
                    timestamp=timestamp,
                    ip_address=ip,
                    event_type=event,
                    severity=severity,
                    status_code=status_code,
                    response_time=round(response_time, 2),
                    message=random.choice(normal_messages),
                )
            )

        # Inject anomalies
        for i in range(50):

            timestamp = now - timedelta(
                minutes=random.randint(0, 1440)
            )

            anomaly_type = i % 3

            if anomaly_type == 0:

                # High response time anomaly
                logs.append(
                    LogEntry(
                        timestamp=timestamp,
                        ip_address=random.choice(ips),
                        event_type="POST /api/payment",
                        severity="ERROR",
                        status_code=500,
                        response_time=random.uniform(3000, 8000),
                        message="Database connection timeout",
                    )
                )

            elif anomaly_type == 1:

                # Critical security anomaly
                logs.append(
                    LogEntry(
                        timestamp=timestamp,
                        ip_address="203.0.113.7",
                        event_type="GET /admin",
                        severity="CRITICAL",
                        status_code=403,
                        response_time=random.uniform(500, 1500),
                        message="Repeated unauthorized access attempt",
                    )
                )

            else:

                # Server failure anomaly
                logs.append(
                    LogEntry(
                        timestamp=timestamp,
                        ip_address=random.choice(ips),
                        event_type="POST /api/login",
                        severity="ERROR",
                        status_code=500,
                        response_time=random.uniform(2500, 6000),
                        message="Authentication service unavailable",
                    )
                )

        LogEntry.objects.bulk_create(logs)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully generated {len(logs)} log entries."
            )
        )