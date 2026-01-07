import time
import uuid

from fastapi import Request

from app.core.logger import get_logger, log_operation

logger = get_logger(__name__)


async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    query_params = request.url.query
    method = request.method
    trace_id = str(uuid.uuid4())
    request.state.trace_id = trace_id

    try:
        response = await call_next(request)
        duration = time.time() - start_time
        status_label = "success" if response.status_code < 400 else "error"

        response.headers["Global-Trace-ID"] = trace_id
        log_operation(
            logger,
            operation="http_request",
            entity_type="request",
            status=status_label,
            details={
                "path": path,
                "method": method,
                "query_params": query_params,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            },
            trace_id=trace_id,
            level="info",
        )
        return response

    except Exception as exc:
        duration = time.time() - start_time
        log_operation(
            logger,
            operation="http_request",
            entity_type="request",
            status="error",
            details={
                "path": path,
                "method": method,
                "query_params": query_params,
                "error": str(exc),
                "duration_ms": round(duration * 1000, 2),
            },
            trace_id=trace_id,
            level="error",
        )
        raise exc
