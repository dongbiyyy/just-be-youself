from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ConflictRule(Base):
    """Configurable rule used by the conflict-detection engine.

    Example rule_type values:
      - "incompatible_positions": position_a / position_b cannot coexist for the same person
        (optionally restricted to the same company or to a parent/subsidiary pair).
    """

    __tablename__ = "conflict_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(32), nullable=False)
    position_a: Mapped[str] = mapped_column(String(32), default="")
    position_b: Mapped[str] = mapped_column(String(32), default="")
    # "same_company" / "parent_subsidiary" / "any"
    scope: Mapped[str] = mapped_column(String(32), default="same_company")
    severity: Mapped[str] = mapped_column(String(16), default="warning")  # info/warning/critical
    description: Mapped[str] = mapped_column(Text, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
