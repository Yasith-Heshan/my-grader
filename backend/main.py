"""
FastAPI Application Entry Point
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import traceback

from routers import teacher, student
from routers import auth
from database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="Python Notebook Grading System",
    description="API for managing assignments, submissions, and grading with MongoDB",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    error_detail = {
        "error": type(exc).__name__,
        "message": str(exc),
        "path": request.url.path,
    }

    # Log the full traceback for debugging
    print(f"\n{'='*60}")
    print(f"ERROR: {type(exc).__name__} at {request.url.path}")
    print(f"{'='*60}")
    traceback.print_exc()
    print(f"{'='*60}\n")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_detail
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors(),
        },
    )


# Include routers
app.include_router(teacher.router, prefix="/api/teacher", tags=["Teacher"])
app.include_router(student.router, prefix="/api/student", tags=["Student"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])


@app.get("/")
async def root():
    return {
        "message": "Python Notebook Grading System API",
        "version": "2.0.0",
        "database": "MongoDB",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "MongoDB"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
