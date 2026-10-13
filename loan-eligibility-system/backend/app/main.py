"""
FastAPI application entry point.
AI-Based Loan Eligibility Assessment System using Forward Chaining Algorithm.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.database import close_db, connect_db
from app.routes import admin, ai, assessment, auth, loans

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: connect DB. Shutdown: close DB."""
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.app_name,
    description=(
        "College demo system combining Agentic AI workflow, "
        "Rule-Based Expert System, Forward Chaining, and Explainable AI. "
        "Eligibility decisions are deterministic and rule-based — not ML."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return user-friendly validation errors."""
    errors = []
    for err in exc.errors():
        loc = " → ".join(str(x) for x in err.get("loc", []))
        errors.append(f"{loc}: {err.get('msg', 'Invalid value')}")
    return JSONResponse(status_code=422, content={"detail": errors})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Never let unhandled exceptions crash the API with stack traces to clients."""
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred. Please try again later."
        },
    )


app.include_router(auth.router)
app.include_router(loans.router)
app.include_router(assessment.router)
app.include_router(ai.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "status": "running",
        "docs": "/docs",
        "message": "Forward Chaining + Agentic AI Loan Eligibility API",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}
