from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


def error_response(
    request: Request,
    status_code: int,
    code: str,
    user_message: str,
    suggestion: str | None = None,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": user_message,
                "user_message": user_message,
                "suggestion": suggestion,
                "details": details,
                "retry_after_seconds": None,
                "request_id": request.headers.get("x-request-id"),
            }
        },
    )
