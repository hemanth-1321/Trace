"""initial_memories_table

Revision ID: 7f5217289466
Revises: 
Create Date: 2026-05-09 18:49:11.961247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID, ARRAY

revision: str = '7f5217289466'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "memories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.String, nullable=False),
        sa.Column("local_image_id", sa.String, nullable=False),
        sa.Column("image_hash", sa.String, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("category", sa.String, nullable=True),
        sa.Column("tags", ARRAY(sa.String), nullable=True),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("status", sa.String, nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP, server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP, server_default=sa.func.now()),
    )

    op.create_index("ix_memories_user_id", "memories", ["user_id"])
    op.create_index("idx_user_local_image", "memories", ["user_id", "local_image_id"], unique=True)
    op.create_index("idx_user_image_hash", "memories", ["user_id", "image_hash"], unique=True)
    op.create_index("idx_user_created_at", "memories", ["user_id", "created_at"])
    op.execute(
        "CREATE INDEX idx_memories_embedding ON memories USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_memories_embedding")
    op.drop_index("idx_user_created_at", table_name="memories")
    op.drop_index("idx_user_image_hash", table_name="memories")
    op.drop_index("idx_user_local_image", table_name="memories")
    op.drop_index("ix_memories_user_id", table_name="memories")
    op.drop_table("memories")
    op.execute("DROP EXTENSION IF EXISTS vector")
