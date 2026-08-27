from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.association import movie_genres, movie_keywords

if TYPE_CHECKING:
    from app.models.genre import Genre
    from app.models.keyword import Keyword


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
        CheckConstraint(
            "vote_count IS NULL OR vote_count >= 0",
            name="ck_movies_vote_count_nonnegative",
        ),
        CheckConstraint(
            "popularity IS NULL OR popularity >= 0",
            name="ck_movies_popularity_nonnegative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    original_title: Mapped[str | None] = mapped_column(String(255))
    overview: Mapped[str | None] = mapped_column(Text)
    tagline: Mapped[str | None] = mapped_column(Text)
    runtime_minutes: Mapped[int | None] = mapped_column(Integer)
    original_language: Mapped[str | None] = mapped_column(String(10), index=True)
    release_year: Mapped[int | None] = mapped_column(Integer, index=True)
    rating: Mapped[float | None] = mapped_column(Float)
    vote_count: Mapped[int | None] = mapped_column(Integer)
    popularity: Mapped[float | None] = mapped_column(Float)
    age_rating: Mapped[str | None] = mapped_column(String(20))
    certification_country: Mapped[str | None] = mapped_column(String(2))
    poster_path: Mapped[str | None] = mapped_column(String(255))
    searchable_description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    genres: Mapped[list["Genre"]] = relationship(
        secondary=movie_genres,
        back_populates="movies",
    )
    keywords: Mapped[list["Keyword"]] = relationship(
        secondary=movie_keywords,
        back_populates="movies",
    )
