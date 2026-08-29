import logging
import argparse

import httpx
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.clients.tmdb import TmdbClient
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.movie_normalizer import normalize_movie
from app.services.movie_repository import upsert_movie


LOGGER = logging.getLogger(__name__)

IMPORT_ERRORS = (
    httpx.HTTPError,
    ValidationError,
    SQLAlchemyError,
)

def import_movies(
        *,
        limit: int,
        minimum_vote_count: int,
) -> None:
    attempted = 0
    created_count = 0
    updated_count = 0
    failed_count = 0
    page = 1
    seen_tmdb_ids: set[int] = set()

    with TmdbClient(
        access_token=(settings.tmdb_read_access_token.get_secret_value()
        ),
    base_url=settings.tmdb_base_url,
    timeout_seconds=settings.tmdb_request_timeout_seconds,
    ) as client:
        while attempted < limit:
            discovery = client.discover_movies(
                page = page,
                minimum_vote_count=minimum_vote_count,
            )

            if not discovery.results:
                break

            for summary in discovery.results:
                if attempted >= limit:
                    break

                if summary.id in seen_tmdb_ids:
                    continue

                seen_tmdb_ids.add(summary.id)
                attempted += 1

                try:
                    details = client.get_movie_details(summary.id)
                    movie_data = normalize_movie(details)

                    with SessionLocal() as session:
                        movie, created = upsert_movie(
                            session,
                            movie_data,
                        )
                        session.commit()

                    if created:
                        created_count += 1
                        action = "created"
                    else:
                        updated_count+=1
                        action="updated"

                    LOGGER.info(
                        "[%s/%s] %s: %s",
                        attempted,
                        limit,
                        action,
                        movie.title,
                    )

                except IMPORT_ERRORS as exc:
                    failed_count += 1
                    LOGGER.warning(
                        "[%s/%s] failed TMDB ID %s: %s",
                        attempted,
                        limit,
                        summary.id,
                        exc,
                    )

            if page >= discovery.total_pages:
                break
            page += 1

    print()
    print("Import complete")
    print(f"Attempted: {attempted}")
    print(f"Created: {created_count}")
    print(f"Updated: {updated_count}")
    print(f"Failed: {failed_count}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import popular movies from TMDB"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of movies to process.",
    )
    parser.add_argument(
        "--minimum-vote-count",
        type=int,
        default=200,
        help="Minimum TMDB vote count.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.limit <= 0:
        raise SystemExit("--limit must be greater than zero")

    if args.minimum_vote_count <0:
        raise SystemExit(
            "--minimum-vote-count cannot be negative"
        )

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )

    import_movies(
        limit=args.limit,
        minimum_vote_count=args.minimum_vote_count,
    )


if __name__ == "__main__":
    main()
