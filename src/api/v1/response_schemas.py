from pydantic import BaseModel


class ResponseSchema[T](BaseModel):
    success: bool
    data: T
    error: str | None = None


class SuccessResponseSchema[T](ResponseSchema[T]):
    success: bool = True
    data: T
    error: str | None = None


class ErrorResponseSchema[T](ResponseSchema[T]):
    success: bool = False
    data: T | None = None
    error: str
