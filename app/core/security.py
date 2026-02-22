from __future__ import annotations

import hmac

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


def require_admin_token(
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> None:
    settings = get_settings()
    expected = (settings.admin_api_token or "").strip()

    # Local dev remains frictionless unless an explicit admin token is configured.
    if not expected and settings.app_env.lower() == "local":
        return

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin endpoints are disabled until ADMIN_API_TOKEN is configured.",
        )

    if not x_admin_token or not hmac.compare_digest(x_admin_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token.",
        )
