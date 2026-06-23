"""In-memory rate limiter for auth and sensitive endpoints. Use Redis in production for multi-replica consistency."""
import time
from collections import defaultdict

from fastapi import Request, HTTPException

# (ip -> list of timestamps in window)
_store: dict[str, list[float]] = defaultdict(list)
# 10 requests per minute per IP for auth
AUTH_WINDOW_SEC = 60
AUTH_MAX_REQUESTS = 10


def _client_ip(request: Request) -> str:
    return request.headers.get("X-Forwarded-For", request.headers.get("X-Real-IP") or "").split(",")[0].strip() or (request.client.host if request.client else "unknown")


def _prune(ts_list: list[float], window_sec: float) -> None:
    now = time.monotonic()
    cutoff = now - window_sec
    while ts_list and ts_list[0] < cutoff:
        ts_list.pop(0)


def check_rate_limit_auth(request: Request) -> None:
    """Raises 429 if the client has exceeded auth rate limit."""
    ip = _client_ip(request)
    now = time.monotonic()
    ts_list = _store[ip]
    _prune(ts_list, AUTH_WINDOW_SEC)
    if len(ts_list) >= AUTH_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests; try again later")
    ts_list.append(now)
