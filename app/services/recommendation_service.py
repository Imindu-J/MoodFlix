from dataclasses import dataclass
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.genre import Genre
from app.models.movie import Movie
from app.schemas.recommendation import (
    RecommendationFilters,
    RecommendationRequest,
    RecommendationItem,
    RecommendationResponse,
    SimilarMoviesRequest,
)
from app.services.embedding_service import EmbeddingService


@dataclass(frozen=True, slots=True)
class RecommendationCandidate:
    movie: Movie
    semantic_similarity: float


class MovieNotFound(LookupError):
    pass

class MovieEmbeddingMissingError(RuntimeError):
    pass


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
    

    def recommend(
            self,
            session: Session,
            request: RecommendationRequest,
    ) -> RecommendationResponse:
        candidates = self.find_candidates(session, request)

        return self._rank_candidates(candidates, limit=request.limit)


    @classmethod
    def _hybrid_score(
        cls,
        candidate: RecommendationCandidate,
    ) -> float:
        semantic_score = max(0.0, candidate.semantic_similarity)
        quality_score = cls._quality_score(candidate.movie)

        return (semantic_score *0.90) + (quality_score * 0.10)

    @staticmethod
    def _quality_score(movie: Movie) -> float:
        if movie.rating is None:
            return 0.0

        vote_count = movie.vote_count or 0
        prior_rating = 6.5
        prior_vote_count = 500

        weighted_rating = (
            (vote_count / (vote_count + prior_vote_count))*movie.rating 
            +(prior_rating/(vote_count + prior_vote_count))*prior_rating
        )

        return weighted_rating / 10

    @classmethod
    def _to_recommendation_item(
        cls, 
        candidate: RecommendationCandidate,        
    ) -> RecommendationItem:
        movie = candidate.movie

        return RecommendationItem(
            tmdb_id=movie.tmdb_id,
            title=movie.title,
            overview=movie.overview,
            release_year=movie.release_year,
            runtime_minutes=movie.runtime_minutes,
            original_language=movie.original_language,
            rating=movie.rating,
            age_rating=movie.age_rating,
            certification_country=movie.certification_country,
            poster_path=movie.poster_path,
            genres=sorted(
                genre.name
                for genre in movie.genres
            ),
            semantic_similarity=round(
                candidate.semantic_similarity,
                6,
            ),
            score=round(
                cls._hybrid_score(candidate),
                6,
            ),
        )

    def _rank_candidates(
            self,
            candidates: list[RecommendationCandidate],
            *,
            limit: int,
    ) -> RecommendationResponse:
        ranked_candidates = sorted(
            candidates,
            key=self._hybrid_score,
            reverse=True,
            )
        
        recommendations = [
            self._to_recommendation_item(candidate)
            for candidate in ranked_candidates[:limit]
        ]

        return RecommendationResponse(recommendations=recommendations)

    def recommend_similar(
            self,
            session: Session,
            tmdb_id: int,
            request: SimilarMoviesRequest,
    ) -> RecommendationResponse:
        source_movie = session.scalar(
            select(Movie).where(Movie.tmdb_id == tmdb_id)
        )

        if source_movie is None:
            raise ModuleNotFoundError(f"Movie with TMDB ID {tmdb_id} was not found.")

        if source_movie.embedding is None:
            raise MovieEmbeddingMissingError(f"Movie {source_movie.title} has no embedding.")

        excluded_tmdb_ids = set(request.exclude_tmdb_ids)
        excluded_tmdb_ids.add(source_movie.tmdb_id)

        candidates = self._find_candidates_by_embedding(
            session=session,
            query_embedding=source_movie.embedding,
            filters=request.filters,
            exclude_tmdb_ids=list(excluded_tmdb_ids),
            candidate_limit=max(request.limit * 10, 50),
        )

        return self._rank_candidates(candidates, limit=request.limit)
