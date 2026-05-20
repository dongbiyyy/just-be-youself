from datetime import date, datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PositionType(str, Enum):
    LEGAL_REPRESENTATIVE = "法定代表人"
    CHAIRMAN = "董事长"
    VICE_CHAIRMAN = "副董事长"
    DIRECTOR = "董事"
    INDEPENDENT_DIRECTOR = "独立董事"
    SUPERVISOR_CHAIR = "监事会主席"
    SUPERVISOR = "监事"
    GENERAL_MANAGER = "总经理"
    DEPUTY_GENERAL_MANAGER = "副总经理"
    CFO = "财务负责人"
    SECRETARY_OF_BOARD = "董事会秘书"
    ACTUAL_CONTROLLER = "实际控制人"
    OTHER = "其他"


class Position(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), index=True, nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    position_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)  # null = 在任
    document_no: Mapped[str] = mapped_column(String(128), default="")
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    person = relationship("Person", back_populates="positions")
    company = relationship("Company", back_populates="positions")
