import time
from typing import Callable, Dict
from threading import Lock
from fastapi import Request, status
from starlette.responses import JSONResponse

from app.core.constants import (
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    RATE_LIMIT_CLEANUP_INTERVAL,
)

_buckets: Dict[str, list] = {}
_lock = Lock()
_last_cleanup = time.time()


async def rate_limit(request: Request, call_next: Callable):
    client_ip = request.client.host if request.client else "anonymous"
    key = f"rl:{client_ip}:{request.url.path}"

    now = time.time()

    with _lock:
        global _last_cleanup
        if now - _last_cleanup > RATE_LIMIT_CLEANUP_INTERVAL:
            expired_keys = [k for k, v in _buckets.items() if v[0] <= now]
            for k in expired_keys:
                del _buckets[k]
            _last_cleanup = now

        if key not in _buckets:
            _buckets[key] = [now + WINDOW_SECONDS, 0]

        reset_at, count = _buckets[key]

        if reset_at <= now:
            reset_at = now + RATE_LIMIT_WINDOW
            count = 0
            _buckets[key] = [reset_at, count]

        if count >= RATE_LIMIT_REQUESTS:
            retry_after = int(reset_at - now)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "title": "Too Many Requests",
                        "description": "Rate limit exceeded.",
                        "translation": "Limite de requisições excedido.",
                        "retry_after_seconds": retry_after,
                    }
                },
                headers={"Retry-After": str(retry_after)},
            )

        count += 1
        _buckets[key][1] = count

        current_count = count
        current_reset = reset_at

    response = await call_next(request)

    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(
        max(RATE_LIMIT_REQUESTS - current_count, 0)
    )
    response.headers["X-RateLimit-Reset"] = str(int(current_reset))

    return response
