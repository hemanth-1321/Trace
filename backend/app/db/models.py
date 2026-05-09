import uuid
from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index, String, TIMESTAMP, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Memory(Base):
    __tablename__ = "memories"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
    )
    local_image_id: Mapped[str]= mapped_column(
        String,
        nullable=False,
    )
    image_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    summary:Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
    )
    tags:Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
    )
    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
    )



Index(
    "idx_user_local_image",
    Memory.user_id,
    Memory.local_image_id,
    unique=True,
)

Index(
    "idx_user_image_hash",
    Memory.user_id,
    Memory.image_hash,
    unique=True,
)