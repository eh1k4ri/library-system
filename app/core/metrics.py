from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request duration in seconds", ["method", "path"]
)


def record_request(
    method: str, path: str, status_code: int, duration_seconds: float
) -> None:
    METHOD = method.upper()
    REQUEST_COUNT.labels(METHOD, path, str(status_code)).inc()
    REQUEST_LATENCY.labels(METHOD, path).observe(duration_seconds)


def render_prometheus() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
