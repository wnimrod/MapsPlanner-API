from logging import getLogger
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
import requests
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.Session import SessionORM
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.settings import settings


router = APIRouter(prefix="/google")

logger = getLogger("app")


class GoogleUserInfo(BaseModel):
    id: str
    email: str
    verified_email: bool
    name: str  # As full name
    given_name: str
    family_name: str
    picture: str  # as URL


class GoogleAuthenticator:
    client_id = settings.google_auth_client_id
    client_secret = settings.google_auth_client_secret
    redirect_uri = "http://localhost:8888/api/auth/google"
    scopes = ["openid", "profile", "email"]

    @classmethod
    def get_login_url(cls):
        return f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={cls.client_id}&redirect_uri={cls.redirect_uri}&scope={'%20'.join(cls.scopes)}&access_type=offline"

    @classmethod
    def get_user_info(cls, code: str) -> GoogleUserInfo:
        token_url = "https://accounts.google.com/o/oauth2/token"
        data = {
            "code": code,
            "client_id": cls.client_id,
            "client_secret": cls.client_secret,
            "redirect_uri": cls.redirect_uri,
            "grant_type": "authorization_code",
        }
        response = requests.post(token_url, data=data)
        access_token = response.json().get("access_token")
        user_info = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        user_info.raise_for_status()

        return GoogleUserInfo(**user_info.json())

    @classmethod
    def create_user(cls, userinfo: GoogleUserInfo) -> UserORM:
        # Convert profile picture to base64
        return UserORM(
            first_name=userinfo.given_name,
            last_name=userinfo.family_name,
            email=userinfo.email,
            profile_picture=userinfo.picture,
            is_active=True,
            is_administrator=False,
        )


@router.get("/")
async def login_google(
    db: AsyncSession = Depends(get_db_session),
    code: Optional[str] = None,
):
    """
    Google OAuth login handler
    """
    if code is None:
        # Redirect to log-in
        return {"url": GoogleAuthenticator.get_login_url()}
    else:
        # Callback with code, get user details
        try:
            userinfo = GoogleAuthenticator.get_user_info(code)
            user_orm, user_created = (
                await UserORM.get_user(db, userinfo.email),
                False,
            )

            if not user_orm:
                logger.info(f"Creating new google user.", extra={"userinfo": userinfo})
                user_orm, user_created = GoogleAuthenticator.create_user(userinfo), True
                db.add(user_orm)
                await db.commit()

            # Set session cookie
            session: str = await SessionORM.create_session(db, user_orm)
            response = RedirectResponse(
                f"{settings.frontend_host}?signed_up={int(user_created)}"
            )
            response.set_cookie(key="token", value=session, secure=True)

            return response

        except requests.exceptions.HTTPError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authentication Failed",
            )
