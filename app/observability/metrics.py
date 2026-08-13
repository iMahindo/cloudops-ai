from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL =Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status_code"]
)

HTTP_REQUEST_ERRORS_TOTAL =Counter(
    "http_requests_errors_total",
    "Total number of failed HTTP requests",
    ["method", "path"]
)

HTTP_REQUEST_DURATION_SECONDS =Histogram(
    "http_requests_duration_seconds",
    "HTTP requests duration in seconds",
    ["method", "path"]
)