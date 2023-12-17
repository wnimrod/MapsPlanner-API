import logging

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from MapsPlanner_API.settings import settings
from MapsPlanner_API.web.api.router import api_router
from importlib import metadata

from MapsPlanner_API.web.lifetime import register_shutdown_event, register_startup_event

__version__ = "0.1.0"  # metadata.version('MapsPlanner_API')


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

    return app
