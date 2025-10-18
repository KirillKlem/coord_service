from prometheus_client import Counter, CollectorRegistry, Gauge, generate_latest

from ..core.config import settings

REGISTRY = CollectorRegistry()

UPLOAD_COUNTER = Counter(
    f"{settings.metrics_namespace}_uploads_total",
    "Total number of uploaded images",
    registry=REGISTRY,
)

PREDICTION_COUNTER = Counter(
    f"{settings.metrics_namespace}_predictions_total",
    "Number of prediction tasks processed",
    registry=REGISTRY,
)

FAILED_PREDICTIONS = Counter(
    f"{settings.metrics_namespace}_predictions_failed_total",
    "Number of prediction tasks that failed",
    registry=REGISTRY,
)

CURRENT_TASKS = Gauge(
    f"{settings.metrics_namespace}_tasks_running",
    "Number of prediction tasks running",
    registry=REGISTRY,
)


def metrics_response() -> bytes:
    return generate_latest(REGISTRY)
