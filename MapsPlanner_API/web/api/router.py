from fastapi.routing import APIRouter

from MapsPlanner_API.web.api.users.views import router as users_router
from MapsPlanner_API.web.api.authentication.router import router as auth_router
from MapsPlanner_API.web.api.trips.views import router as trips_router
from MapsPlanner_API.web.api.markers.router import router as markers_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(trips_router)
api_router.include_router(markers_router)
