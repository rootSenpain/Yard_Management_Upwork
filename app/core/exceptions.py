from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

async def global_exception_handler(request: Request, exc: Exception):
    """
    Sistemde fırlatılan tüm beklenmedik (500) hataları yakalar.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected internal server error occurred.",
            "detail": str(exc) if True else None  # Geliştirme aşamasında str(exc) faydalıdır
        },
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    HTTPException (404, 401, 403, 400) hatalarını yakalar ve şık bir formatta döner.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        },
    )