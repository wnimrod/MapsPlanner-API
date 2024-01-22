from datetime import datetime
from typing import List, Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel

from MapsPlanner_API.db.models.AuditLog import AuditLogORM, EAuditAction
from MapsPlanner_API.db.models.types import TTarget
from MapsPlanner_API.web.api.query_filters.date_range import DateRangeFilterMixin


class AuditLog(BaseModel):
    id: int
    creation_date: datetime
    action: EAuditAction
    user_id: int
    target: TTarget


class AuditFilter(DateRangeFilterMixin, Filter):
    action__in: Optional[List[EAuditAction]] = None
    target_model__in: Optional[List[str]] = None
    target_id__in: Optional[List[int]] = None

    class Constants(Filter.Constants):
        model = AuditLogORM
