from datetime import datetime

from pydantic import BaseModel

from MapsPlanner_API.db.models.AuditLog import EAuditAction
from MapsPlanner_API.db.models.types import TTarget


class AuditLog(BaseModel):
    id: int
    creation_date: datetime
    action: EAuditAction
    user_id: int
    target: TTarget
