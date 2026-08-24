Setup, AI, Coding Approach, Assumptions, and Limitations**.

## 1. Setup

### Prerequisites

* Python 3.10+
* Django
* pip
* Git

### Installation

```bash
git clone https://github.com/yashchavan-cmpn-coder/LOG_MANAGER.git
cd LOG_MANAGER

python -m venv venv
```

### Activate Virtual Environment

**Windows:**

```powershell
venv\Scripts\activate
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Database Setup

```bash
python manage.py migrate
```

### Run the Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 2. AI / Anomaly Detection

LOG_MANAGER uses an automated anomaly detection approach to identify unusual or potentially problematic log entries.

The system analyzes log information such as:

* Log severity
* Error frequency
* Repeated errors
* Critical events
* Time-based patterns
* Error bursts
* Similar or recurring log messages

A severity-based scoring mechanism is used to prioritize important events.

Example:

| Severity | Score |
| -------- | ----: |
| INFO     |     0 |
| WARNING  |     1 |
| ERROR    |     3 |
| CRITICAL |     5 |

The system combines these signals to determine whether a log event should be treated as an anomaly.

The goal is not only to detect errors but also to **identify abnormal behavior and prioritize events that require attention**.

---

## 3. Coding Approach

The project follows a modular Django architecture.

### Backend

Django is responsible for:

* Request handling
* URL routing
* Business logic
* Database operations
* Authentication
* Anomaly detection
* API/view processing

### Database

The application stores structured log information and detected anomalies using Django models.

Typical flow:

```text
Log Input
    ↓
Log Validation
    ↓
Log Processing
    ↓
Severity Analysis
    ↓
Anomaly Detection
    ↓
Anomaly Record
    ↓
Dashboard / API
```

### Code Organization

The anomaly detection logic is separated from the Django views wherever possible.

For example:

```text
models.py
    ↓
stores log/anomaly data

views.py
    ↓
handles HTTP requests

anomaly detection/service logic
    ↓
processes logs and calculates anomaly scores
```

This separation makes the application easier to maintain, test, and extend.

### Error Handling

The system validates incoming log data before processing it.

Invalid or unsupported severity values are rejected instead of being silently processed.

Transactions can be used for operations that modify multiple database records to maintain data consistency.

---

## 4. Assumptions

The project is developed with the following assumptions:

1. Log entries contain a valid timestamp.
2. Each log entry has a recognizable severity level.
3. Severity values follow predefined categories such as `INFO`, `WARNING`, `ERROR`, and `CRITICAL`.
4. Log messages are sufficiently descriptive for analysis.
5. The incoming log data follows the expected structure.
6. The database is available while processing logs.
7. The initial anomaly detection rules are suitable for the expected log patterns.
8. The system assumes that a sudden increase in errors can indicate abnormal behavior.
9. The severity score represents the relative importance of an event.
10. The system is intended to assist monitoring rather than completely replace human investigation.

---

## 5. Limitations

The current implementation has some limitations:

### Rule-Based Detection

The anomaly detection system primarily depends on predefined rules and scoring rather than a fully trained machine-learning model.

Therefore, it may not detect complex anomalies that are not covered by the existing rules.

### False Positives

Some events may be classified as anomalies even though they are legitimate.

For example:

```text
A scheduled maintenance operation
        ↓
Large number of ERROR logs
        ↓
System detects unusual error frequency
        ↓
Possible anomaly
```

The event may actually be expected behavior.

### False Negatives

An unusual event may not be detected if it does not violate the predefined detection rules.

### Limited Historical Learning

The current system does not continuously learn from historical logs to automatically update its anomaly detection thresholds.

### Log Format Dependency

The system expects logs to follow the supported structure. Completely different log formats may require additional parsing logic.

### Scalability

For very large production environments with millions of logs per day, additional infrastructure such as:

* PostgreSQL
* Redis
* Celery
* Kafka
* Elasticsearch/OpenSearch

could be introduced to improve processing and scalability.

### Context Awareness

The system analyzes available log information but may not understand the complete business context behind an event.

---

## 6. Future Improvements

Potential improvements include:

* Machine-learning-based anomaly detection
* Real-time log streaming
* Automatic threshold learning
* Log clustering
* Natural-language log summarization
* Alert notifications
* Email/Slack alerts
* Elasticsearch/OpenSearch integration
* Redis and Celery for background processing
* Advanced analytics dashboards
* Historical anomaly trend analysis
* Root-cause analysis
* Container and cloud log integration

---

## Overall Architecture

```text
                    LOG_MANAGER
                         │
                         ▼
                  Log Input / API
                         │
                         ▼
                  Data Validation
                         │
                         ▼
                  Log Processing
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Severity Analysis       Pattern Analysis
              │                     │
              └──────────┬──────────┘
                         ▼
                 Anomaly Detection
                         │
                         ▼
                  Anomaly Scoring
                         │
                         ▼
                    Database
                         │
                         ▼
                 Django Dashboard
                         │
                         ▼
              Developer / Admin
```

This README gives an interviewer a clear picture of **how to install the project, how the detection works, how the code is structured, what assumptions you made, and where the system can be improved**.
