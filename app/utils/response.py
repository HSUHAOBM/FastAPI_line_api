from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any


def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """
    統一的成功回應格式
    """

    return JSONResponse(
        status_code=status_code,
        content={
            "ok": True,
            "data": data,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


def fail_response(message: str = "Error", errors: Any = None, status_code: int = 400):
    """
    統一的失敗回應格式
    """

    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "errors": errors,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


def register_exception_handlers(app: FastAPI):
    """
    註冊全域的錯誤處理器
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return fail_response(
            message="Validation Error",
            errors=exc.errors(),
            status_code=422
        )

    # @app.exception_handler(HTTPException)
    # async def http_exception_handler(request: Request, exc: HTTPException):
    #     return fail_response(
    #         message=exc.detail,
    #         errors=None,
    #         status_code=exc.status_code
    #     )
