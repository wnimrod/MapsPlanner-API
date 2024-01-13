from typing import List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.users.schema import User, UserDetails


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
async def test_user_details(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    users: List[UserORM],
):
    target_user = users[0]
    url = fastapi_app.url_path_for("user_details", user_id=target_user.id)

    async def test_success(session: SessionORM, admin: bool):
        response = await client.get(
            url,
            params={"impersonate_user_id": "all"},
            cookies={"token": session.token},
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), "Failed to fetch user details."
        expected_user_details = await UserDetails.build_from_orm(dbsession, target_user)
        actual_user_details = UserDetails(**response.json())
        assert (
            expected_user_details == actual_user_details
        ), "User details does not match."

    # Test 1: Make sure authorized user gets profiles
    session, *other_sessions = await target_user.awaitable_attrs.sessions
    await test_success(session, admin=False)

    # Test 2: Get another user, it should not have access to target user profile.
    another_user = users[1]
    session, *other_sessions = await another_user.awaitable_attrs.sessions
    response = await client.get(
        url,
        params={"impersonate_user_id": "all"},
        cookies={"token": session.token},
    )
    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), "Data leak: User details where fetched to unauthorized user."

    # Test 3: Administrator can access the data, anyway
    another_user.is_administrator = True
    dbsession.add(another_user)
    await dbsession.commit()
    await test_success(session, admin=True)


@pytest.mark.anyio
async def test_update_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    users: List[UserORM],
):
    ...
    # target_user = users[0]
    # url = fastapi_app.url_path_for("update_user", user_id=target_user.id)
    #
    # session, *other_sessions = await target_user.awaitable_attrs.sessions
    # changes = UserUpdateRequest(first_name="Changed")
    # response = await client.patch(url, json=changes, cookies={"token": session.token})
    #
