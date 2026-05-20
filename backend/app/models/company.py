from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
    credit_code: Mapped[Optional[str]] = mapped_column(String(32), unique=True, index=True)
    short_name: Mapped[str] = mapped_column(String(128), default="")
    legal_representative: Mapped[str] = mapped_column(String(64), default="")
    reg_capital: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    reg_capital_currency: Mapped[str] = mapped_column(String(8), default="CNY")
    established_date: Mapped[Optional[date]] = mapped_column(Date)
    reg_address: Mapped[str] = mapped_column(String(512), default="")
    business_scope: Mapped[str] = mapped_column(Text, default="")
    company_type: Mapped[str] = mapped_column(String(64), default="")  # 有限责任公司、股份有限公司...
    status: Mapped[str] = mapped_column(String(16), default="active")  # active / dissolved
    parent_company_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"), index=True
    )
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    parent: Mapped[Optional["Company"]] = relationship(
        "Company", remote_side="Company.id", backref="children"
    )
    positions: Mapped[List["Position"]] = relationship(  # noqa: F821
        "Position", back_populates="company", cascade="all,delete-orphan"
    )
