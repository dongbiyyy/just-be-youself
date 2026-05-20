from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ShareholderType(str, Enum):
    PERSON = "person"
    COMPANY = "company"


class Shareholding(Base):
    """Polymorphic shareholder: either a Person or a Company holds shares of a Company."""

    __tablename__ = "shareholdings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    shareholder_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    # Refers to persons.id when type=person, companies.id when type=company.
    shareholder_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    ratio: Mapped[Optional[float]] = mapped_column(Numeric(8, 4))  # 0~100 percentage
    amount: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(8), default="CNY")
    contribute_method: Mapped[str] = mapped_column(String(32), default="货币")
    contribute_date: Mapped[Optional[date]] = mapped_column(Date)
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
