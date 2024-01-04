import json

from datetime import datetime
from pathlib import Path
from typing import Any, AsyncGenerator, List

import pytest
from _pytest.fixtures import FixtureRequest
from fastapi import FastAPI
from httpx import AsyncClient

from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.settings import settings
from MapsPlanner_API.web.application import get_app
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.utils import create_database, drop_database


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from MapsPlanner_API.db.meta import meta  # noqa: WPS433
    from MapsPlanner_API.db.models import load_all_models  # noqa: WPS433

    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()
        await drop_database()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin_nested()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
def fastapi_app(
    dbsession: AsyncSession,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    application.dependency_overrides[get_db_session] = lambda: dbsession
    return application  # noqa: WPS331


@pytest.fixture
async def client(
    fastapi_app: FastAPI, anyio_backend: Any
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(app=fastapi_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def users(dbsession: AsyncSession, request: FixtureRequest) -> List[UserORM]:
    """
    Populate database with mock users.
    """

    with open(
        Path(request.config.rootpath, "MapsPlanner_API/tests/fixtures/users.json")
    ) as mock_file:
        mock_users: List[dict] = json.load(mock_file)

    orm_users: List[UserORM] = []

    for mock_user in mock_users:
        register_date = datetime.fromisoformat(mock_user.pop("register_date"))
        user = UserORM(**mock_user, register_date=register_date)
        orm_users.append(user)
        dbsession.add(user)

    await dbsession.commit()

    return orm_users
