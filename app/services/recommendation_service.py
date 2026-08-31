from dataclasses import dataclass
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.genre import Genre
from app.models.movie import Movie
from app.schemas.recommendation import RecommendationFilters, RecommendationRequest
from app.services.embedding_service import EmbeddingService


@dataclass(frozen=True, slots=True)
class RecommendationCandidate:
    movie: Movie
    semantic_similarity: float


class RecommendationService:
    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service

    def find_candidates(self, session: Session, request: RecommendationRequest) -> list[RecommendationCandidate]:
        query_embedding = self.embedding_service.encode_query(request.query)
        candidate_limit = max(request.limit * 10, 50)

        return self._find_candidates_by_embedding(
            session=session,
            query_embedding=query_embedding,
            filters=request.filters,
            exclude_tmdb_ids=request.exclude_tmdb_ids,
            candidate_limit=candidate_limit,
        )

    def _find_candidates_by_embedding(
            self,
            session: Session,
            query_embedding: list[float],
            filters: RecommendationFilters,
            exclude_tmdb_ids: list[int],
            candidate_limit: int,
    ) -> list[RecommendationCandidate]:
        distance = Movie.embedding.cosine_distance(query_embedding)
        statement = (
            select(Movie, distance.label("distance"))
            .options(selectinload(Movie.genres))
            .where(Movie.embedding.is_not(None))
        )

        statement = self._apply_filters(statement, filters)

        if exclude_tmdb_ids:
            statement = statement.where(Movie.tmdb_id.not_in(exclude_tmdb_ids))

        statement = statement.order_by(distance).limit(candidate_limit)

        rows = session.execute(statement).all()

        return [
            RecommendationCandidate(
                movie=movie,
                semantic_similarity=self._similarity_from_distance(distance_value)
            )
            for movie, distance_value in rows
        ]

    @staticmethod
    def _apply_filters(statement: Select, filters: RecommendationFilters) -> Select:
        genre_names = {
            genre.strip().lower()
            for genre in filters.genres_any
            if genre.strip()
        }

        if genre_names:
            statement = statement.where(Movie.genres.any(
                func.lower(Genre.name).in_(genre_names)
            ))

        languages = {
            language.strip().lower()
            for language in filters.original_languages_any
            if language.strip()
        }

        if languages:
            statement = statement.where(
                func.lower(Movie.original_language).in_(languages)
            )

        age_ratings = {
            rating.strip().upper()
            for rating in filters.age_ratings_any
            if rating.strip()
        }

        if age_ratings:
            statement = statement.where(
                func.upper(Movie.age_rating).in_(age_ratings)
            )

        if filters.maximum_runtime_minutes is not None:
            statement = statement.where(
                Movie.runtime_minutes
                <= filters.maximum_runtime_minutes
            )

        if filters.minimum_release_year is not None:
            statement = statement.where(
                Movie.release_year
                >= filters.minimum_release_year
            )

        if filters.maximum_release_year is not None:
            statement = statement.where(
                Movie.release_year
                <= filters.maximum_release_year
            )

        if filters.minimum_rating is not None:
            statement = statement.where(
                Movie.rating >= filters.minimum_rating
            )

        if filters.minimum_vote_count is not None:
            statement = statement.where(
                Movie.vote_count
                >= filters.minimum_vote_count
            )

        return statement

    @staticmethod
    def _similarity_from_distance(distance: float) -> float:
        similarity = 1 - float(distance)
        return max(-1.0, min(1.0, similarity))

