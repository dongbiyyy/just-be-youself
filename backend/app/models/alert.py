from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AlertStatus(str, Enum):
    OPEN = "open"
    ACK = "acknowledged"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class Alert(Base):
    """Risk / reminder item shown on the dashboard."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    # "conflict" / "term_expiry" / "other"
    severity: Mapped[str] = mapped_column(String(16), default="warning")
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    detail: Mapped[str] = mapped_column(Text, default="")
    related_entity_type: Mapped[str] = mapped_column(String(32), default="")
    related_entity_id: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default=AlertStatus.OPEN.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
