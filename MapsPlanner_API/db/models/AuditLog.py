import importlib
from datetime import datetime
from enum import IntEnum
from pydoc import locate
from typing import Optional, TypedDict

from sqlalchemy import Integer, JSON, ForeignKey, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, AsyncAttrs, AsyncSessionTransaction
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import ChoiceType

from MapsPlanner_API.db.base import Base as BaseORM
from MapsPlanner_API.db.connection import get_session
from MapsPlanner_API.db.models.User import UserORM
from MapsPlanner_API.db.models.types import TTarget, TChanges


class EAuditAction(IntEnum):
    Creation = 1
    Modification = 2
    Deletion = 3
    ChatGPTQuery = 4


class ExtraFieldMapping(TypedDict):
    target: TTarget
    changes: dict[str, TChanges]


class AuditLogORM(AsyncAttrs, BaseORM):
    """
    Logs important actions that made on the system.
    """

    __tablename__ = "audit"

    id: Mapped[int] = mapped_column(primary_key=True)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    action: Mapped[EAuditAction] = mapped_column(
        ChoiceType(EAuditAction, impl=Integer())
    )
    extra: Mapped[ExtraFieldMapping] = mapped_column(
        JSON(none_as_null=True), nullable=True
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    user: Mapped[UserORM] = relationship(UserORM, back_populates="audit_logs")

    @classmethod
    def _build_extra(
        cls,
        target: Optional[BaseORM] = None,
        changes: Optional[TChanges] = None,
    ):
        """
        helper to build up the extra field, based on common parameters that might be provided.
        """

        extra = {}
        if target:
            extra["target"] = {
                "model": f"{target.__class__.__name__}",
                "id": target.id,
            }
        if changes:
            extra["changes"] = changes

        return extra

    @classmethod
    async def log(
        cls,
        db: AsyncSession,
        action: EAuditAction,
        *,
        user: Optional[UserORM] = None,
        target: Optional[BaseORM] = None,
        changes: Optional[TChanges] = None,
        **extra,
    ) -> "AuditLogORM":
        extra.update(cls._build_extra(target, changes))
        audit_log = cls(action=action, user_id=user.id, extra=extra)
        db.add(audit_log)
        await db.commit()
        return audit_log

    @property
    async def instance(self) -> Optional[BaseORM]:
        """
        Returns the instance of the object associated with this audit log.
        """

        if target := self.extra.get("target"):
            model = locate(f"MapsPlanner_API.db.models.{target['model']}")
            async with get_session() as db:
                return await db.get(model, target["id"])

    async def to_api(self) -> "AuditLog":
        from MapsPlanner_API.web.api.audit.schema import AuditLog

        return AuditLog(
            id=self.id,
            creation_date=self.creation_date,
            action=self.action,
            user_id=self.user_id,
            target=self.extra.get("target"),
        )
