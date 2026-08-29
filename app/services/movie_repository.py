from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.genre import Genre
from app.models.keyword import Keyword
from app.models.movie import Movie
from app.schemas.movie_import import ImportedTerm, MovieImport


def upsert_movie(
    session: Session,
    movie_data: MovieImport,
) -> tuple[Movie, bool]:
    movie = session.scalar(
        select(Movie).where(Movie.tmdb_id == movie_data.tmdb_id)
    )

    values = movie_data.model_dump(
        exclude={"genres", "keywords"}
    )

    created = movie is None

    if movie is None:
        movie = Movie(**values)
        session.add(movie)
    else:
        for field_name, value in values.items():
            setattr(movie, field_name, value)

    movie.genres = _upsert_genres(session, movie_data.genres)
    movie.keywords = _upsert_keywords(session, movie_data.keywords)

    session.flush()
    return movie, created


def _upsert_genres(
    session: Session,
    terms: list[ImportedTerm],
) -> list[Genre]:
    if not terms:
        return []

    tmdb_ids = [term.tmdb_id for term in terms]

    existing = session.scalars(
        select(Genre).where(Genre.tmdb_id.in_(tmdb_ids))
    ).all()

    genres_by_tmdb_id = {
        genre.tmdb_id: genre
        for genre in existing
    }

    genres: list[Genre] = []

    for term in terms:
        genre = genres_by_tmdb_id.get(term.tmdb_id)

        if genre is None:
            genre = Genre(
                tmdb_id=term.tmdb_id,
                name=term.name,
            )
            session.add(genre)
            genres_by_tmdb_id[term.tmdb_id] = genre
        else:
            genre.name = term.name

        genres.append(genre)

    return genres


def _upsert_keywords(
    session: Session,
    terms: list[ImportedTerm],
) -> list[Keyword]:
    if not terms:
        return []

    tmdb_ids = [term.tmdb_id for term in terms]

    existing = session.scalars(
        select(Keyword).where(Keyword.tmdb_id.in_(tmdb_ids))
    ).all()

    keywords_by_tmdb_id = {
        keyword.tmdb_id: keyword
        for keyword in existing
    }

    keywords: list[Keyword] = []

    for term in terms:
        keyword = keywords_by_tmdb_id.get(term.tmdb_id)

        if keyword is None:
            keyword = Keyword(
                tmdb_id=term.tmdb_id,
                name=term.name,
            )
            session.add(keyword)
            keywords_by_tmdb_id[term.tmdb_id] = keyword
        else:
            keyword.name = term.name

        keywords.append(keyword)

    return keywords
