from typing import List, Annotated

from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from MapsPlanner_API.db.dependencies import get_db_session
from MapsPlanner_API.db.models.AuditLog import AuditLogORM
from MapsPlanner_API.web.api.audit.schema import AuditLog, AuditFilter
from MapsPlanner_API.web.api.dependencies import get_queryset


router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/")
async def audit_logs(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    query: Annotated[Select, Depends(get_queryset(AuditLogORM))],
    audit_filter: Annotated[AuditFilter, FilterDepends(AuditFilter)],
) -> List[AuditLog]:
    query = audit_filter.filter(query)

    audit_logs_result = await db.execute(query)
    audit_logs: List[AuditLogORM] = audit_logs_result.scalars()

    return [await audit_log.to_api() for audit_log in audit_logs]
