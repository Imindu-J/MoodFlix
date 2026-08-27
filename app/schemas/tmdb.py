from pydantic import BaseModel, ConfigDict, Field


class TmdbModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class TmdbMovieSummary(TmdbModel):
    id: int
    title: str
    vote_count: int = 0
    vote_average: float = 0
    popularity: float = 0

class TmdbDiscoverResponse(TmdbModel):
    page: int
    total_pages: int
    results: list[TmdbMovieSummary] = Field(default_factory=list)


class TmdbGenre(TmdbModel):
    id: int
    name: str


class TmdbKeyword(TmdbModel):
    id: int
    name: str


class TmdbKeywordResponse(TmdbModel):
    keywords: list[TmdbKeyword] = Field(default_factory=list)


class TmdbReleaseDate(TmdbModel):
    certification: str = ""
    release_type: int = Field(alias="type")


class TmdbReleaseCountry(TmdbModel):
    iso_3166_1: str
    release_dates: list[TmdbReleaseDate] = Field(default_factory=list)


class TmdbReleaseDatesResponse(TmdbModel):
    results: list[TmdbReleaseCountry] = Field(default_factory=list)


class TmdbMovieDetails(TmdbModel):
    id: int
    title: str
    original_title: str | None = None
    overview: str | None = None
    tagline: str | None = None
    runtime: int | None = None
    original_language: str | None = None
    release_date: str | None = None
    vote_average: float | None = None
    vote_count: int | None = None
    popularity: float | None = None
    poster_path: str | None = None
    genres: list[TmdbGenre] = Field(default_factory=list)
    keywords: TmdbKeywordResponse = Field(
        default_factory=TmdbKeywordResponse
    )
    release_dates: TmdbReleaseDatesResponse = Field(
        default_factory=TmdbReleaseDatesResponse
    )

