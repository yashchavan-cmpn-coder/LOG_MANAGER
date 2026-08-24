from django.db import models

# Create your models here.
from django.db import models


class LogEntry(models.Model):
    SEVERITY_CHOICES = [
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    timestamp = models.DateTimeField()
    ip_address = models.GenericIPAddressField()
    event_type = models.CharField(max_length=100)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )
    status_code = models.IntegerField()
    response_time = models.FloatField(default=0)
    message = models.TextField()

    is_anomaly = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.timestamp} - {self.event_type}"


class Anomaly(models.Model):
    log = models.OneToOneField(
        LogEntry,
        on_delete=models.CASCADE,
        related_name="anomaly"
    )

    score = models.FloatField()
    reason = models.TextField()

    ai_explanation = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    recommended_action = models.TextField(blank=True)

    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anomaly - {self.log.id} - Score: {self.score}"