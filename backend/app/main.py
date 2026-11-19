import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.routers import (
    analyze_router,
    papers_router,
    upload_router,
    history_router,
    export_router,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("research_scope")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database schema; embedding models load only when an analysis needs them."""
    logger.info("Starting Research Scope API Server...")
    try:
        init_db()
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error("Failed to initialize database on startup: %s", e)

    yield
    logger.info("Shutting down Research Scope API Server...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Mount API Routers
app.include_router(analyze_router, prefix=settings.API_V1_STR)
app.include_router(papers_router, prefix=settings.API_V1_STR)
app.include_router(upload_router, prefix=settings.API_V1_STR)
app.include_router(history_router, prefix=settings.API_V1_STR)
app.include_router(export_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": settings.VERSION,
    }


@app.get("/api/status")
def model_status():
    """Returns whether the embedding engine can serve requests and its loading state."""
    from app.nlp.embeddings import embedding_engine
    return {
        "status": "healthy",
        "model_ready": embedding_engine.is_ready,
        "model_loading": embedding_engine.model_loading,
        "version": settings.VERSION,
    }


# Wrap the complete FastAPI app so CORS headers are also applied to error responses.
app = CORSMiddleware(
    app=app,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type", "Origin", "X-Requested-With"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
