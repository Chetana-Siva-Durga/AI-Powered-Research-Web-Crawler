from app.routers.analyze import router as analyze_router
from app.routers.papers import router as papers_router
from app.routers.upload import router as upload_router
from app.routers.history import router as history_router
from app.routers.export import router as export_router

__all__ = [
    "analyze_router",
    "papers_router",
    "upload_router",
    "history_router",
    "export_router",
]
