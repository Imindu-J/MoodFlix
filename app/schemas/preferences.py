from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.recommendation import RecommendationFilters


class PreferenceIntent(StrEnum):
    SEARCH = "search"
    SIMILAR = "similar"


class ExtractionStatus(StrEnum):
    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"


class ExtractedPreferences(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    status: ExtractionStatus
    intent: PreferenceIntent = PreferenceIntent.SEARCH

    semantic_query: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )
    reference_movie_title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    filters: RecommendationFilters = Field(
        default_factory=RecommendationFilters
    )
    limit: int = Field(default=5, ge=3, le=5)

    clarification_question: str | None = Field(
        default=None,
        min_length=1,
        max_length=300,
    )

    @model_validator(mode="after")
    def validate_extraction(self) -> Self:
        if self.status == ExtractionStatus.NEEDS_CLARIFICATION:
            if self.clarification_question is None:
                raise ValueError(
                    "A clarification question is required"
                )

            return self

        if self.intent == PreferenceIntent.SIMILAR:
            if self.reference_movie_title is None:
                raise ValueError(
                    "A reference movie is required for similar searches"
                )

            return self

        has_filters = any(self.filters.model_dump().values())

        if self.semantic_query is None and not has_filters:
            raise ValueError(
                "A search needs a semantic query or metadata filter"
            )

        return self
