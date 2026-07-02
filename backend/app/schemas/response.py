from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ErrorDetail | None = None


def success_response(data: T) -> ApiResponse[T]:
    return ApiResponse(success=True, data=data)


def error_response(code: str, message: str) -> ApiResponse[None]:
    return ApiResponse(success=False, error=ErrorDetail(code=code, message=message))
