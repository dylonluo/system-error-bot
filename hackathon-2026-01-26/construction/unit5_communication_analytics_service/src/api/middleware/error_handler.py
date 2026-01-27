from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from ...application.dtos import ErrorResponse


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    error_response = ErrorResponse(
        error="Validation Error",
        details=str(exc.errors())
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.dict()
    )


async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    error_response = ErrorResponse(
        error="Bad Request",
        details=str(exc)
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.dict()
    )


async def permission_error_handler(request: Request, exc: PermissionError):
    """Handle permission errors."""
    error_response = ErrorResponse(
        error="Forbidden",
        details=str(exc)
    )
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=error_response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    error_response = ErrorResponse(
        error="Internal Server Error",
        details=str(exc)
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )
