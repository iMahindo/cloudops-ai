from fastapi import Request
from uuid import uuid4
from time import perf_counter
from opentelemetry import trace

from structlog.contextvars import bind_contextvars, clear_contextvars
from app.core.logging import get_logger
from app.observability.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUEST_ERRORS_TOTAL,  HTTP_REQUESTS_TOTAL

logger = get_logger(__name__)

async def request_context_middleware(request: Request, call_next):
    clear_contextvars()

    request_id = str(uuid4())

    #get the current span and set the request_id as attribute
    span = trace.get_current_span()
    span.set_attribute("request_id", request_id)

    #get trace_id to set in the context for logging
    span_context = span.get_span_context()

    if span_context.is_valid:
        #format to hex because is an int
        trace_id = format(span_context.trace_id, "032x")

        bind_contextvars(request_id=request_id,trace_id=trace_id)
    else:
        bind_contextvars(request_id=request_id)

    #calculate the duration
    start_time = perf_counter()

    #initializate the status code
    status_code = 500

    try:
        response =  await call_next(request)

        status_code = response.status_code

        #duration * 1000 to transform in ms
        duration_ms = (perf_counter() - start_time ) * 1000
        
        #exclude the metrics logs when  it works ok
        if request.url.path != "/metrics":
            logger.info(
                    "http_request_completed",
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=round(duration_ms, 2)
                )
        
        #add the request_id to header for trazability
        response.headers["X-Request-ID"] = request_id

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
    
        raise

    finally:
        #exclude the prometheus calls to metrics in the metrics calculate
        if request.url.path != "/metrics":
            #Exclude the mtrics when it is ok
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                path=request.url.path,
                status_code=str(status_code),
            ).inc()

            #need in seconds for prometheus
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                path=request.url.path,
            ).observe(duration_ms / 1000)

            if status_code >= 400:
                HTTP_REQUEST_ERRORS_TOTAL.labels(
                    method=request.method,
                    path=request.url.path,
                ).inc()
