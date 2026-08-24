from django.urls import path

from . import views


app_name = "logs"


urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path(
        "anomaly/<int:anomaly_id>/",
        views.anomaly_detail,
        name="anomaly_detail",
    ),
    path(
    "anomaly/<int:anomaly_id>/generate-ai/",
    views.generate_ai_analysis,
    name="generate_ai_analysis",
),

    path(
    "upload/",
    views.upload_csv,
    name="upload_csv",
),
]