import time
from typing import Any, Optional
from threading import RLock

MAX_CACHE_SIZE = 1000

_store: dict[str, tuple[float, Any]] = {}
_lock = RLock()


def get_cache(key: str) -> Optional[Any]:
    now = time.time()
    with _lock:
        item = _store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < now:
            _store.pop(key, None)
            return None
        return value


def set_cache(key: str, value: Any, ttl_seconds: int = 300) -> None:
    expires_at = time.time() + ttl_seconds
    with _lock:
        if len(_store) >= MAX_CACHE_SIZE:
            _store.clear()

        _store[key] = (expires_at, value)


def clear_cache(key: str) -> None:
    with _lock:
        _store.pop(key, None)
