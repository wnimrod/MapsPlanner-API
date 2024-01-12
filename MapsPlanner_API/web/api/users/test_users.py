from typing import List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.users.schema import User


@pytest.mark.anyio
async def test_current_user(
    monkeypatch: MonkeyPatch,
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    users: List[UserORM],
):
    user = users[0]
    session = await SessionORM.create_session(dbsession, user)
    url = fastapi_app.url_path_for("current_user")

    # Test 1: Make sure request without session is not passing
    response = await client.get(url)
    assert (
        response.status_code == status.HTTP_401_UNAUTHORIZED
    ), "Authentication passed without credentials.."

    # Test 2: Make sure not every token gives access.
    response = await client.get(url, cookies={"token": "thisisatoken!!!"})
    assert (
        response.status_code == status.HTTP_401_UNAUTHORIZED
    ), "Authentication passed with wrong credentials."

    # Test 3: Try to authenticate and get the user.
    response = await client.get(url, cookies={"token": session.token})
    assert response.status_code == status.HTTP_200_OK, "Authentication failed."

    # Test 3: The requested user is retrieved.
    response_user = User(**response.json())
    assert response_user == user.to_api()


@pytest.mark.anyio
async def test_user_details():
    ...


@pytest.mark.anyio
async def test_update_user():
    ...
