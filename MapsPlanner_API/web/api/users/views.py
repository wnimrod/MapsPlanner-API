from logging import getLogger
from typing import Annotated, Optional


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import AuditLogORM, EAuditLog
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.dependencies import (
    TAuditLogger,
    get_audit_logger,
    get_current_user,
)
from MapsPlanner_API.web.api.users.schema import User, UserDetails, UserUpdateRequest
from MapsPlanner_API.web.api.users.utils import validate_request

logger = getLogger("app")

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/current")
async def current_user(user: Annotated[UserORM, Depends(get_current_user)]) -> User:
    """
    Returns details of the currently connected user
    """
    return user.to_api()


@router.get("/{user_id}")
async def user_details(
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user_id: int,
) -> UserDetails:
    validate_request(user, user_id)

    if user := await db.get(UserORM, user_id):
        return await UserDetails.build_from_orm(db, user)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Such user."
        )


@router.patch("/{user_id}")
async def update_user(
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    audit: Annotated[TAuditLogger, Depends(get_audit_logger)],
    user_id: int,
    payload: UserUpdateRequest,
):
    validate_request(user, user_id)

    update_fields = payload.model_dump(exclude_none=True)
    target_user = await db.get(UserORM, user_id)
    changes = target_user.diff(update_fields)
    target_user.assign(update_fields)

    db.add(target_user)
    await db.commit()

    await audit(action=EAuditLog.Modification, target=target_user, changes=changes)
    return user.to_api()
