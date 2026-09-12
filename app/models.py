from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Racket(Base):
    __tablename__ = "rackets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    level: Mapped[str] = mapped_column(String(30), default="unknown", index=True)
    style: Mapped[str] = mapped_column(String(30), default="balanced", index=True)
    shape: Mapped[str] = mapped_column(String(30), index=True)
    weight_text: Mapped[str] = mapped_column(String(50))
    weight_avg: Mapped[float] = mapped_column(Float)
    balance_text: Mapped[str] = mapped_column(String(50))
    balance_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    balance_group: Mapped[str] = mapped_column(String(20), default="unknown", index=True)
    price_text: Mapped[str] = mapped_column(String(40))
    source_name: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
