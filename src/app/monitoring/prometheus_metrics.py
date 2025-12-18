from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
import os


def setup_prometheus(app):
    """
    Configure Prometheus pour FastAPI

    Args:
        app: Instance FastAPI
    """
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    print("✅ Prometheus metrics enabled at /metrics")
