from fastapi.routing import APIRouter
from MapsPlanner_API.web.api import echo
from MapsPlanner_API.web.api import monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
