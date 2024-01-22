from fastapi.routing import APIRouter

from MapsPlanner_API.web.api.audit.views import router as audit_router
from MapsPlanner_API.web.api.authentication.views import router as auth_router
from MapsPlanner_API.web.api.markers.views import router as markers_router
from MapsPlanner_API.web.api.trips.views import router as trips_router
from MapsPlanner_API.web.api.users.views import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(trips_router)
api_router.include_router(markers_router)
api_router.include_router(audit_router)
