from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.association import movie_keywords

if TYPE_CHECKING:
    from app.models.movie import Movie


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_keywords,
        back_populates="keywords",
    )
