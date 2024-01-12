from typing import List

import pytest
import requests.exceptions
from _pytest.monkeypatch import MonkeyPatch
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.settings import settings
from MapsPlanner_API.utils import raise_
from MapsPlanner_API.web.api.authentication.google_auth import (
    GoogleAuthenticator,
    GoogleUserInfo,
)

from requests.exceptions import HTTPError


@pytest.mark.anyio
async def test_authentication_link(fastapi_app: FastAPI, client: AsyncClient) -> None:
    url = fastapi_app.url_path_for("login_google")
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["url"] == GoogleAuthenticator.get_login_url()


@pytest.mark.anyio
@pytest.mark.parametrize("user_exists", [True, False])
@pytest.mark.parametrize("user_auto_approval", [True, False])
async def test_authentication_success(
    monkeypatch: MonkeyPatch,
    fastapi_app: FastAPI,
    client: AsyncClient,
    users: List[UserORM],
    dbsession: AsyncSession,
    user_exists: bool,
    user_auto_approval: bool,
):
    mock_user_info = GoogleUserInfo(
        id="somefakeid",
        email="fake@email.com",
        verified_email=True,
        name="Fake User",
        given_name="Fake",
        family_name="user",
        picture="",
    )

    monkeypatch.setattr(
        GoogleAuthenticator,
        "get_user_info",
        lambda code: mock_user_info,
    )

    monkeypatch.setattr(settings, "user_auto_approval", user_auto_approval)

    if user_exists:
        user: UserORM = GoogleAuthenticator.create_user(mock_user_info)
        dbsession.add(user)
        await dbsession.commit()

    url = fastapi_app.url_path_for("login_google")
    response = await client.get(url, params={"code": "authcode"})

    get_user_query = select(UserORM).where(UserORM.email == mock_user_info.email)
    result = await dbsession.execute(get_user_query)
    result = result.scalars().all()
    user = result[0]

    # Test 1: Make sure user created and only once

    assert not len(result) < 1, "New logged-in user not exist in db."
    assert not len(result) > 1, f"Multiple users with email {user.email} created."

    # Test 2: Make sure we got the right token
    user_tokens = [session.token for session in await user.awaitable_attrs.sessions]
    response_token = response.cookies["token"]

    assert response_token in user_tokens, "Invalid token returned."

    # Test 3: User activation as needed
    assert (
        True if user_exists else user.is_active == user_auto_approval
    ), "Wrong user active state"


@pytest.mark.anyio
async def test_authentication_failed(
    monkeypatch: MonkeyPatch, fastapi_app: FastAPI, client: AsyncClient
):
    monkeypatch.setattr(
        GoogleAuthenticator,
        "get_user_info",
        lambda code: raise_(HTTPError()),
    )

    url = fastapi_app.url_path_for("login_google")
    response = await client.get(url, params={"code": "authcode"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
