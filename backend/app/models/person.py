from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    # ID card is stored only as one-way hash plus last-4 plaintext for search.
    id_card_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    id_card_last4: Mapped[str] = mapped_column(String(4), index=True, default="")
    nationality: Mapped[str] = mapped_column(String(32), default="中国")
    phone: Mapped[str] = mapped_column(String(32), default="")
    email: Mapped[str] = mapped_column(String(128), default="")
    gender: Mapped[str] = mapped_column(String(8), default="")
    remark: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    positions: Mapped[List["Position"]] = relationship(  # noqa: F821
        "Position", back_populates="person", cascade="all,delete-orphan"
    )
