from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models import SessionORM

from .google_auth import router as google_auth_router

router = APIRouter(prefix="/auth", tags=["Authentication"])
router.include_router(google_auth_router)


@router.get("/logout")
async def logout(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    request: Request,
    response: Response,
):
    token = request.cookies.get("token")
    session: Optional[SessionORM] = await db.get(SessionORM, token)
    if session:
        await db.delete(session)
        response.delete_cookie("token")
        return {"logged_out": True}
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"logged_out": False}
