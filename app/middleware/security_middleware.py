from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Iterable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


@dataclass(frozen=True)
class RateLimitRule:
    path_prefix: str
    limit_per_minute: int


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_bytes: int):
        super().__init__(app)
        self.max_body_bytes = max_body_bytes

    async def dispatch(self, request: Request, call_next):
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return await call_next(request)

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > self.max_body_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": (
                                f"Request body too large. Maximum is {self.max_body_bytes} bytes."
                            )
                        },
                    )
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length."})

        body = await request.body()
        if len(body) > self.max_body_bytes:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": f"Request body too large. Maximum is {self.max_body_bytes} bytes."
                },
            )

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive  # type: ignore[attr-defined]
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        default_limit_per_minute: int,
        rules: Iterable[RateLimitRule],
    ):
        super().__init__(app)
        self.default_limit_per_minute = max(1, default_limit_per_minute)
        self.rules = tuple(rules)
        self.window_seconds = 60.0
        self._events: dict[tuple[str, str], deque[float]] = {}
        self._lock = threading.Lock()

    def _extract_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip() or "unknown"
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    def _limit_for_path(self, path: str) -> int:
        for rule in self.rules:
            if path.startswith(rule.path_prefix):
                return max(1, rule.limit_per_minute)
        return self.default_limit_per_minute

    def _is_allowed(self, client_ip: str, path: str, limit: int) -> tuple[bool, int]:
        now = time.monotonic()
        key = (client_ip, path)

        with self._lock:
            history = self._events.setdefault(key, deque())
            while history and now - history[0] >= self.window_seconds:
                history.popleft()

            if len(history) >= limit:
                retry_after = max(1, int(self.window_seconds - (now - history[0])))
                return False, retry_after

            history.append(now)
            return True, 0

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        limit = self._limit_for_path(path)
        client_ip = self._extract_client_ip(request)

        allowed, retry_after = self._is_allowed(client_ip, path, limit)
        if not allowed:
            return JSONResponse(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content={
                    "detail": "Rate limit exceeded.",
                    "limit_per_minute": limit,
                    "retry_after_seconds": retry_after,
                },
            )

        return await call_next(request)
