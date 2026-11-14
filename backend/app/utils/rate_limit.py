from collections import OrderedDict, deque
from threading import Lock
from time import monotonic

from fastapi import Request

from app.configs.settings import get_settings
from app.utils.exceptions import AppError

attempts: OrderedDict[str, deque] = OrderedDict()
register_attempts: OrderedDict[str, deque] = OrderedDict()
lock = Lock()


def limit_login(request: Request):
    """Per-process IP limit. Use a shared gateway limit for multiple workers."""
    settings = get_settings()
    key = request.client.host if request.client else "unknown"
    now = monotonic()
    with lock:
        bucket = attempts.setdefault(key, deque())
        attempts.move_to_end(key)
        while bucket and bucket[0] <= now - settings.app_login_window_seconds:
            bucket.popleft()
        if len(bucket) >= settings.app_login_rate_limit:
            raise AppError(429, "Too many attempts", {"auth": "Wait before trying again"})
        bucket.append(now)
        if len(attempts) > 10000:
            attempts.popitem(last=False)


def limit_register(request: Request):
    """Separate public-registration bucket; does not consume login attempts."""
    settings = get_settings()
    key = request.client.host if request.client else "unknown"
    now = monotonic()
    with lock:
        bucket = register_attempts.setdefault(key, deque())
        register_attempts.move_to_end(key)
        while bucket and bucket[0] <= now - settings.app_register_window_seconds:
            bucket.popleft()
        if len(bucket) >= settings.app_register_rate_limit:
            raise AppError(429, "Too many attempts", {"auth": "Wait before trying again"})
        bucket.append(now)
        if len(register_attempts) > 10000:
            register_attempts.popitem(last=False)
