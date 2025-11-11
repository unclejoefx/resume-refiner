"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import upload, analyze, export

app = FastAPI(
    title="Resume Refiner API",
    description="AI-powered resume analysis and optimization",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(export.router, prefix="/api/export", tags=["export"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Resume Refiner API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
