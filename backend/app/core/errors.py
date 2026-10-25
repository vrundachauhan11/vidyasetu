"""Standard application exceptions and error handlers."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.logging_config import logger


class VidyaSetuException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundError(VidyaSetuException):
    """Entity was not found in the repository."""
    def __init__(self, entity_name: str, identifier: str):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"entity": entity_name, "identifier": identifier},
        )


class ValidationFailedError(VidyaSetuException):
    """Data intake or rule validation failed."""
    def __init__(self, message: str, errors: list = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": errors or []},
        )


async def vidyasetu_exception_handler(request: Request, exc: VidyaSetuException) -> JSONResponse:
    """Format custom domain exceptions consistently."""
    logger.warning(f"Domain exception on {request.method} {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": type(exc).__name__,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all unexpected error handler without leaking internal stack details."""
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "type": "InternalServerError",
                "message": "An internal regulatory processing error occurred. Please consult the system audit log.",
                "details": {},
            },
        },
    )
