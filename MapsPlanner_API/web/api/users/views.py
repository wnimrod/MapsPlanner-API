from logging import getLogger
from typing import Annotated

import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import EAuditAction
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.web.api.dependencies import (
    TAuditLogger,
    get_audit_logger,
    get_current_user,
    get_queryset,
)
from MapsPlanner_API.web.api.users.schema import User, UserDetails, UserUpdateRequest


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/current")
async def current_user(user: Annotated[UserORM, Depends(get_current_user)]) -> User:
    """
    Returns details of the currently connected user
    """
    return user.to_api()


@router.get("/{user_id}")
async def user_details(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    query: Annotated[Select, Depends(get_queryset(UserORM))],
    user_id: int,
) -> UserDetails:
    query = query.where(UserORM.id == user_id)

    try:
        user: UserORM = (await db.execute(query)).scalar_one()
    except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.MultipleResultsFound):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Such user.",
        )

    return await UserDetails.build_from_orm(db, user)


@router.patch("/{user_id}")
async def update_user(
    user: Annotated[UserORM, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    audit: Annotated[TAuditLogger, Depends(get_audit_logger)],
    query: Annotated[Select, Depends(get_queryset(UserORM))],
    user_id: int,
    payload: UserUpdateRequest,
):
    query = query.where(UserORM.id == user_id)
    update_fields = payload.model_dump(exclude_none=True)

    try:
        target_user = (await db.execute(query)).scalar_one()
    except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.MultipleResultsFound):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Such user.",
        )

    changes = target_user.diff(update_fields)
    target_user.assign(update_fields)

    db.add(target_user)
    await db.commit()

    await audit(action=EAuditAction.Modification, target=target_user, changes=changes)
    return user.to_api()
