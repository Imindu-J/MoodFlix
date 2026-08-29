"""add movie embedding hsnw index

Revision ID: 15d69ea39f5f
Revises: 03270bb8bca6
Create Date: 2026-08-29 10:23:03.502243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15d69ea39f5f'
down_revision: Union[str, Sequence[str], None] = '03270bb8bca6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_movies_embedding_hsnw",
        "movies",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_with={"m":16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_movies_embedding_hnsw", table_name="movies")
