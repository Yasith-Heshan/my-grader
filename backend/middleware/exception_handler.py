from fastapi import Request, logger, status
from fastapi.responses import JSONResponse

from backend.exeptions import DuplicateResourceError, ResourceNotFoundError


async def exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except DuplicateResourceError as e:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "duplicate_resource",
                "message": str(e),
                "resource_type": e.resource_type,
                "identifier": e.identifier
            }
        )
    except ResourceNotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "not_found", "message": str(e)}
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "validation_error", "message": str(e)}
        )
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "internal_error", "message": "An unexpected error occurred"}
        )