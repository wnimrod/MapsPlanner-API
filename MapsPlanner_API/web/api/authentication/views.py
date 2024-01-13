from fastapi import APIRouter

from .google_auth import router as google_auth_router

router = APIRouter(prefix="/auth", tags=["Authentication"])
router.include_router(google_auth_router)
