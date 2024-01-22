from typing import List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.users.schema import User, UserDetails, UserUpdateRequest


@pytest.mark.anyio
async def test_current_user(
    monkeypatch: MonkeyPatch,
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    access_token: SessionORM,
    users: List[UserORM],
):
    url = fastapi_app.url_path_for("current_user")
    access_user = await access_token.awaitable_attrs.user

    # Test 1: Make sure request without session is not passing
    response = await client.get(url, cookies={"token": access_token.token})
    expected_response_code = (
        status.HTTP_200_OK if access_user else status.HTTP_401_UNAUTHORIZED
    )
    assert response.status_code == expected_response_code

    if access_user:
        # Test 2: Try to get the current user.
        response_user = User(**response.json())
        assert response_user == access_user.to_api()


@pytest.mark.asyncio
@pytest.mark.parametrize("impersonate_user_id", [True, False])
async def test_users_list(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    users: List[UserORM],
    access_token: SessionORM,
    impersonate_user_id: bool,
):
    url = fastapi_app.url_path_for("users_list")
    access_user = await access_token.awaitable_attrs.user

    response = await client.get(
        url,
        params={"impersonate_user_id": "all"} if impersonate_user_id else {},
        cookies={"token": access_token.token},
    )

    # 1. Test response code is fine.
    expected_status_code = (
        status.HTTP_200_OK if access_user else status.HTTP_401_UNAUTHORIZED
    )
    assert response.status_code == expected_status_code
    # 2. Test Response content is right
    if response.status_code == status.HTTP_200_OK:
        if access_user.is_administrator and impersonate_user_id is True:
            expected_users = [
                user.to_api().model_dump()
                for user in sorted(users, key=lambda user: user.id, reverse=True)
            ]
        else:
            expected_users = [access_user.to_api().model_dump()]

        assert response.json() == expected_users, "Unexpected users response."


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
@pytest.mark.parametrize("modify_another_user", [True, False])
async def test_update_user(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    access_token: SessionORM,
    modify_another_user: bool,
    users: List[UserORM],
):
    access_user = await access_token.awaitable_attrs.user
    target_user = users[1] if modify_another_user or not access_user else access_user

    url = fastapi_app.url_path_for("update_user", user_id=target_user.id)
    changes = UserUpdateRequest(first_name="Changed").model_dump(exclude_none=True)
    response = await client.patch(
        url,
        json=changes,
        cookies={"token": access_token.token},
        params={"impersonate_user_id": "all"} if modify_another_user else {},
    )

    # 1. Test access control
    if access_user is None:
        expected_status_code = status.HTTP_401_UNAUTHORIZED
    elif access_user.id != target_user.id and not access_user.is_administrator:
        expected_status_code = status.HTTP_404_NOT_FOUND
    else:
        expected_status_code = status.HTTP_200_OK

    assert response.status_code == expected_status_code

    if expected_status_code == status.HTTP_200_OK:
        # 2. Test Data changed
        updated_user = {**target_user.to_api().model_dump(), **changes}
        assert response.json() == updated_user
