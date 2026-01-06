import time
from fastapi import Request
from typing import Callable
from app.core.metrics import record_request


async def metrics(request: Request, call_next: Callable):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    record_request(request.method, request.url.path, response.status_code, duration)
    return response
