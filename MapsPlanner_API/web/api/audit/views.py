from typing import List, Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import AuditLogORM, EAuditAction
from MapsPlanner_API.web.api.audit.schema import AuditLog
from MapsPlanner_API.web.api.dependencies import get_queryset

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/")
async def audit_logs(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    query: Annotated[Select, Depends(get_queryset(AuditLogORM))],
    action: Optional[EAuditAction] = None,
    target_model: Optional[str] = None,
    target_id: Optional[int] = None,
) -> List[AuditLog]:
    if action is not None:
        query = query.where(AuditLogORM.action == action)
    if target_model is not None:
        query = query.where(
            AuditLogORM.extra["target", "model"].as_string() == target_model
        )
    if target_id is not None:
        query = query.where(AuditLogORM.extra["target", "id"].as_integer() == target_id)

    audit_logs_result = await db.execute(query)
    audit_logs: List[AuditLogORM] = audit_logs_result.scalars()

    return [await audit_log.to_api() for audit_log in audit_logs]
