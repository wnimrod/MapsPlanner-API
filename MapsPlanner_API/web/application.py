from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware

from MapsPlanner_API.settings import settings
from MapsPlanner_API.web.api.router import api_router

from MapsPlanner_API.web.lifetime import register_shutdown_event, register_startup_event

from MapsPlanner_API import __version__


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="MapsPlanner_API",
        version=__version__,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    allow_origins = [
        settings.frontend_url,
        settings.backend_url,
        f"https://{settings.host}:${settings.port}",
        f"http://{settings.host}:${settings.port}",
    ]

    # Register middlewares
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
