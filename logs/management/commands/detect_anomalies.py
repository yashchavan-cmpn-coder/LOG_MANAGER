from django.core.management.base import BaseCommand

from logs.anamoly import detect_anomalies


class Command(BaseCommand):
    help = "Detect anomalous log entries"

    def handle(self, *args, **options):

        result = detect_anomalies()

        self.stdout.write(
            self.style.SUCCESS(
                f"Analyzed {result['total']} logs."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Detected {result['anomalies']} anomalies."
            )
        )