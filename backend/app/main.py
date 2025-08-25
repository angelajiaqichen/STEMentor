from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await create_tables()
    yield
    # Shutdown
    pass


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI-powered learning platform with intelligent content processing",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add trusted host middleware
    if settings.ALLOWED_HOSTS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS
        )

    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_STR)

    @app.get("/")
    async def root():
        return {
            "message": "AI Learning Platform API",
            "version": settings.VERSION,
            "docs": "/docs"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_application()
