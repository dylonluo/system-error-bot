"""Error handling middleware."""

from fastapi import Request, status
from fastapi.responses import JSONResponse


async def error_handler_middleware(request: Request, call_next):
    """Global error handler middleware."""
    try:
        response = await call_next(request)
        return response
    except ValueError as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": "Bad Request", "message": str(e)})
    except PermissionError as e:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"error": "Forbidden", "message": str(e)})
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Internal Server Error", "message": str(e)}
        )
