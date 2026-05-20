from fastapi import APIRouter

from .auth import router as auth_router
from .companies import router as companies_router
from .persons import router as persons_router
from .positions import router as positions_router
from .shareholdings import router as shareholdings_router
from .imports import router as imports_router
from .search import router as search_router
from .dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(companies_router)
api_router.include_router(persons_router)
api_router.include_router(positions_router)
api_router.include_router(shareholdings_router)
api_router.include_router(imports_router)
api_router.include_router(search_router)
api_router.include_router(dashboard_router)
