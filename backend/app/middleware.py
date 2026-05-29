"""Simple in-memory rate limiting middleware (no Redis dependency)."""

import time
from collections import defaultdict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import get_settings

settings = get_settings()

_requests: dict[str, list[float]] = defaultdict(list)


async def rate_limit_middleware(request: Request, call_next):
    """Sliding-window rate limiter per IP for API routes."""
    path = request.url.path

    # Skip non-API routes and health
    if not path.startswith("/api/") or path in ("/api/health",):
        return await call_next(request)

    # Determine client IP
    ip = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()

    now = time.time()
    window = 60
    max_req = settings.RATE_LIMIT_PER_MINUTE
    cutoff = now - window

    # Prune expired entries and check limit
    _requests[ip] = [t for t in _requests[ip] if t > cutoff]
    if len(_requests[ip]) >= max_req:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Try again later.",
                "code": "rate_limited",
            },
            headers={"Retry-After": "60"},
        )

    _requests[ip].append(now)

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(max_req)
    response.headers["X-RateLimit-Remaining"] = str(
        max_req - len(_requests[ip])
    )
    return response


def setup_middleware(app: FastAPI):
    """Register rate-limiter middleware."""
    app.middleware("http")(rate_limit_middleware)
