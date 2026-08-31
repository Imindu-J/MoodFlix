from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RecommendationFilters(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    genres_any: list[str] = Field(default_factory=list)
    original_languages_any: list[str] = Field(default_factory=list)
    age_ratings_any: list[str] = Field(default_factory=list)
    maximum_runtime_minutes: int | None = Field(default=None, gt=0)
    minimum_release_year: int | None = Field(default=None, ge=1878, le=2030)
    maximum_release_year: int | None = Field(default=None, ge=1878, le=2030)
    minimum_rating: float | None = Field(default=None, ge=0, le=10)
    minimum_vote_count: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_year_range(self) -> Self:
        if self.minimum_release_year is not None and self.maximum_release_year is not None and self.minimum_release_year > self.maximum_release_year:
            raise ValueError("minimum_release_year cannot exceed maximum_release_year")
        return self


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=500)
    filters: RecommendationFilters = Field(
        default_factory=RecommendationFilters
    )
    exclude_tmdb_ids: list[int] = Field(default_factory=list)
    limit: int = Field(default=5, ge=3, le=5)


class SimilarMoviesRequest(BaseModel):
    filters: RecommendationFilters = Field(
        default_factory=RecommendationFilters
    )
    exclude_tmdb_ids: list[int] = Field(default_factory=list)
    limit: int = Field(default=5, ge=3, le=5)


class RecommendationItem(BaseModel):
    tmdb_id: int
    title: str
    overview: str | None
    release_year: int | None
    runtime_minutes: int | None
    original_language: str | None
    rating: float | None
    age_rating: str | None
    certification_country: str | None
    poster_path: str | None
    genres: list[str]

    semantic_similarity: float
    score: float


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
