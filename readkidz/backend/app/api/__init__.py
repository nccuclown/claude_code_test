"""
ReadKidz Platform - API Routes
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .projects import router as projects_router
from .generation import router as generation_router
from .templates import router as templates_router
from .users import router as users_router

router = APIRouter()

# Include all routers
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(projects_router, prefix="/projects", tags=["Projects"])
router.include_router(generation_router, prefix="/generate", tags=["AI Generation"])
router.include_router(templates_router, prefix="/templates", tags=["Templates & Styles"])
