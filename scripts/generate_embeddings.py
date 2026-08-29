import argparse

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.movie import Movie
from app.services.embedding_service import EmbeddingService


def generate_embeddings(
    *,
    batch_size: int,
    limit: int | None,
    refresh: bool,
) -> None:
    service = EmbeddingService()

    statement = (
        select(Movie)
        .where(Movie.searchable_description.is_not(None))
        .order_by(Movie.id)
    )

    if not refresh:
        statement = statement.where(Movie.embedding.is_(None))

    if limit is not None:
        statement = statement.limit(limit)

    with SessionLocal() as session:
        movies = list(session.scalars(statement))

        if not movies:
            print("No movies require embeddings.")
            return

        completed = 0
        total = len(movies)

        for start in range(0, total, batch_size):
            batch = movies[start : start + batch_size]

            texts = [
                movie.searchable_description
                for movie in batch
                if movie.searchable_description is not None
            ]

            embeddings = service.encode(
                texts,
                batch_size=batch_size,
            )

            for movie, embedding in zip(
                batch,
                embeddings,
                strict=True,
            ):
                movie.embedding = embedding

            session.commit()

            completed += len(batch)
            print(f"Embedded {completed}/{total} movies")

    print("Embedding generation complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate embeddings for MoodFlix movies.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Regenerate embeddings that already exist.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.batch_size <= 0:
        raise SystemExit("--batch-size must be greater than zero")

    if args.limit is not None and args.limit <= 0:
        raise SystemExit("--limit must be greater than zero")

    generate_embeddings(
        batch_size=args.batch_size,
        limit=args.limit,
        refresh=args.refresh,
    )


if __name__ == "__main__":
    main()
