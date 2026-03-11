"""CodeEcoScan — FastAPI application entrypoint.

Creates and configures the FastAPI application instance, registers
routers, and installs global exception handlers.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router as analysis_router
from app.core.config import get_settings
from app.core.exceptions import AnalysisError, CodeParsingError
from app.db.database import init_db

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Static analysis service that inspects Python code using the AST "
        "module to extract structural patterns related to energy risk."
    ),
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize the database on startup."""
    init_db()


# ---------------------------------------------------------------
# CORS — allow all origins so browser frontends can access the API
# ---------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# ---------------------------------------------------------------
# Router registration
# ---------------------------------------------------------------

app.include_router(analysis_router)

# ---------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------


@app.exception_handler(CodeParsingError)
async def code_parsing_error_handler(
    _request: Request, exc: CodeParsingError
) -> JSONResponse:
    """Return a 400 response when submitted code has syntax errors.

    Uses the ``ErrorResponse`` JSON schema for consistency.
    """
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message},
    )


@app.exception_handler(AnalysisError)
async def analysis_error_handler(
    _request: Request, exc: AnalysisError
) -> JSONResponse:
    """Return a 500 response for unexpected analysis failures.

    In production, ``exc.message`` is generic to avoid leaking
    internals.  Enable ``DEBUG=true`` for verbose messages.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message},
    )


# ---------------------------------------------------------------
# Health check
# ---------------------------------------------------------------


@app.get(
    "/health",
    summary="Service health check",
    response_model=dict[str, str],
)
async def health_check() -> dict[str, str]:
    """Return service health status."""
    return {"status": "healthy"}
