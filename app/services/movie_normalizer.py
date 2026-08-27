from datetime import date

from app.schemas.movie_import import ImportedTerm, MovieImport
from app.schemas.tmdb import TmdbMovieDetails

CERTIFICATION_PREFERENCES = ("LK", "US", "GB")
RELEASE_TYPE_PRIORITY = {
    3: 0,  # Theatrical
    2: 1,  # Theatrical limited
    4: 2,  # Digital
    5: 3,  # Physical
    6: 4,  # TV
    1: 5,  # Premiere
}


def normalize_movie(details: TmdbMovieDetails) -> MovieImport:
    genres = _normalize_terms(
        [(genre.id, genre.name) for genre in details.genres]
    )
    keywords = _normalize_terms(
        [(keyword.id, keyword.name) for keyword in details.keywords.keywords]
    )

    release_year = _extract_release_year(details.release_date)
    runtime = details.runtime if details.runtime and details.runtime > 0 else None
    age_rating, certification_country = _select_certification(details)

    searchable_description = _build_searchable_description(
        details=details,
        genres=genres,
        keywords=keywords,
        release_year=release_year,
        runtime=runtime,
        age_rating=age_rating,
        certification_country=certification_country,
    )

    return MovieImport(
        tmdb_id=details.id,
        title=details.title,
        original_title=_clean_optional(details.original_title),
        overview=_clean_optional(details.overview),
        tagline=_clean_optional(details.tagline),
        runtime_minutes=runtime,
        original_language=_clean_optional(details.original_language),
        release_year=release_year,
        rating=details.vote_average,
        vote_count=details.vote_count,
        popularity=details.popularity,
        age_rating=age_rating,
        certification_country=certification_country,
        poster_path=_clean_optional(details.poster_path),
        searchable_description=searchable_description,
        genres=genres,
        keywords=keywords,
    )


def _normalize_terms(values: list[tuple[int, str]]) -> list[ImportedTerm]:
    terms: list[ImportedTerm] = []
    seen_ids: set[int] = set()

    for tmdb_id, name in values:
        cleaned_name = name.strip()

        if tmdb_id <= 0 or not cleaned_name or tmdb_id in seen_ids:
            continue

        seen_ids.add(tmdb_id)
        terms.append(ImportedTerm(tmdb_id=tmdb_id, name=cleaned_name))

    return terms


def _extract_release_year(value: str | None) -> int | None:
    if not value:
        return None

    try:
        return date.fromisoformat(value).year
    except ValueError:
        return None


def _select_certification(
    details: TmdbMovieDetails,
) -> tuple[str | None, str | None]:
    countries = {
        result.iso_3166_1.upper(): result
        for result in details.release_dates.results
    }

    for country_code in CERTIFICATION_PREFERENCES:
        country = countries.get(country_code)

        if country is None:
            continue

        release_dates = sorted(
            country.release_dates,
            key=lambda item: RELEASE_TYPE_PRIORITY.get(
                item.release_type,
                99,
            ),
        )

        for release in release_dates:
            certification = release.certification.strip()

            if certification:
                return certification, country_code

    return None, None


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned or None


def _build_searchable_description(
    *,
    details: TmdbMovieDetails,
    genres: list[ImportedTerm],
    keywords: list[ImportedTerm],
    release_year: int | None,
    runtime: int | None,
    age_rating: str | None,
    certification_country: str | None,
) -> str:
    parts = [f"Title: {details.title}."]

    if details.original_title and details.original_title != details.title:
        parts.append(f"Original title: {details.original_title}.")

    if release_year:
        parts.append(f"Release year: {release_year}.")

    if genres:
        parts.append(
            f"Genres: {', '.join(term.name for term in genres)}."
        )

    if runtime:
        parts.append(f"Runtime: {runtime} minutes.")

    if details.original_language:
        parts.append(
            f"Original language code: {details.original_language}."
        )

    if details.vote_average is not None:
        parts.append(f"TMDB user rating: {details.vote_average:.1f}/10.")

    if age_rating and certification_country:
        parts.append(
            f"Age certification: {age_rating} "
            f"({certification_country})."
        )

    if details.tagline:
        parts.append(f"Tagline: {details.tagline.strip()}")

    if details.overview:
        parts.append(f"Plot: {details.overview.strip()}")

    if keywords:
        parts.append(
            f"Keywords: {', '.join(term.name for term in keywords)}."
        )

    return " ".join(parts)
