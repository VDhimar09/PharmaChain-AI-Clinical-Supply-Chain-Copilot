import time

from fastapi import Request
from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "pharmachain_http_requests_total",
    "Total number of HTTP requests handled by the PharmaChain API.",
    ["method", "route", "status"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "pharmachain_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "route"],
)

HTTP_ERRORS_TOTAL = Counter(
    "pharmachain_http_errors_total",
    "Total number of HTTP 4xx and 5xx responses.",
    ["method", "route", "status"],
)


async def metrics_middleware(request: Request, call_next):
    """Record safe, low-cardinality HTTP metrics."""

    if request.url.path == "/metrics":
        return await call_next(request)

    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start

    route = request.scope.get("route")
    route_path = getattr(route, "path", request.url.path)

    method = request.method
    status = str(response.status_code)

    HTTP_REQUESTS_TOTAL.labels(
        method=method,
        route=route_path,
        status=status,
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        method=method,
        route=route_path,
    ).observe(duration)

    if response.status_code >= 400:
        HTTP_ERRORS_TOTAL.labels(
            method=method,
            route=route_path,
            status=status,
        ).inc()

    return response