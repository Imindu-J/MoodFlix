from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        CheckConstraint(
            "runtime_minutes IS NULL OR runtime_minutes > 0",
            name="ck_movies_runtime_positive",
        ),
        CheckConstraint(
            "rating IS NULL OR (rating >= 0 AND rating <= 10)",
            name="ck_movies_rating_range",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    overview: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[list[str]] = mapped_column(ARRAY(String(50)), default=list)
    runtime_minutes: Mapped[int | None] = mapped_column(Integer)
    original_language: Mapped[str | None] = mapped_column(String(10), index=True)
    release_year: Mapped[int | None] = mapped_column(Integer, index=True)
    rating: Mapped[float | None] = mapped_column(Float)
    age_rating: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
