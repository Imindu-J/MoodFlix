from pydantic import BaseModel, ConfigDict, Field


class ImportedTerm(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tmdb_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=255)


class MovieImport(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tmdb_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    original_title: str | None = None
    overview: str | None = None
    tagline: str | None = None
    runtime_minutes: int | None = Field(default=None, gt=0)
    original_language: str | None = Field(default=None, max_length=10)
    release_year: int | None = Field(default=None, ge=1878, le=2100)
    rating: float | None = Field(default=None, ge=0, le=10)
    vote_count: int | None = Field(default=None, ge=0)
    popularity: float | None = Field(default=None, ge=0)
    age_rating: str | None = Field(default=None, max_length=20)
    certification_country: str | None = Field(
        default=None,
        min_length=2,
        max_length=2,
    )
    poster_path: str | None = Field(default=None, max_length=255)
    searchable_description: str = Field(min_length=1)
    genres: list[ImportedTerm] = Field(default_factory=list)
    keywords: list[ImportedTerm] = Field(default_factory=list)
