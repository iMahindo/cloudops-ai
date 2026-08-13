from fastapi import Request
from uuid import uuid4
from time import perf_counter

from structlog.contextvars import bind_contextvars, clear_contextvars
from app.core.logging import get_logger
from app.observability.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUEST_ERRORS_TOTAL,  HTTP_REQUESTS_TOTAL

logger = get_logger(__name__)

async def request_context_middleware(request: Request, call_next):
    clear_contextvars()

    request_id = str(uuid4())

    bind_contextvars(request_id=request_id)

    #calculate the duration
    start_time = perf_counter()

    try:
        response =  await call_next(request)

        #duration * 1000 to transform in ms
        duration_ms = (perf_counter() - start_time ) * 1000

        logger.info(
            "http_request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2)
        )

        #add the request_id to header for trazability
        response.headers["X-Request-ID"] = request_id

        #update the metrics
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            path=request.url.path,
            status_code=str(response.status_code)
        ).inc()

        #need in seconds for prometheus
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            path=request.url.path
        ).observe(duration_ms / 1000)

        return response

    except Exception:
        #duration * 1000 to transform in ms
        duration_ms = (perf_counter() - start_time ) * 1000

        logger.exception(
            "http_request_failed",
            method=request.method,
            path=request.url.path,
            duration_ms=round(duration_ms, 2)
        )

        #update the metrics
        HTTP_REQUEST_ERRORS_TOTAL.labels(
            method=request.method,
            path=request.url.path,
        ).inc()

        #increment the total requests too
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            path=request.url.path,
            status_code="500",
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            path=request.url.path
        ).observe(duration_ms / 1000)
    
        raise
        
