"""Memory service operations."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Memory


async def create_memory(
    db: AsyncSession,
    user_id: str,
    local_image_id: str,
    image_hash: str,
    summary: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[list[str]] = None,
    embedding: Optional[list[float]] = None,
) -> Memory:
    """Create a new memory record."""
    memory = Memory(
        user_id=user_id,
        local_image_id=local_image_id,
        image_hash=image_hash,
        summary=summary,
        category=category,
        tags=tags,
        embedding=embedding,
        status="active",
    )
    db.add(memory)
    await db.flush()
    await db.refresh(memory)
    return memory


async def get_memory_by_id(
    db: AsyncSession,
    memory_id: UUID,
    user_id: str,
) -> Optional[Memory]:
    """Fetch memory by ID, scoped to user."""
    stmt = select(Memory).where(
        (Memory.id == memory_id) & (Memory.user_id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_memories_by_user(
    db: AsyncSession,
    user_id: str,
    limit: int = 50,
    offset: int = 0,
) -> list[Memory]:
    """Fetch all memories for a user."""
    stmt = (
        select(Memory)
        .where(Memory.user_id == user_id)
        .order_by(Memory.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_memory_by_hash(
    db: AsyncSession,
    user_id: str,
    image_hash: str,
) -> Optional[Memory]:
    """Fetch memory by image hash, scoped to user."""
    stmt = select(Memory).where(
        (Memory.user_id == user_id) & (Memory.image_hash == image_hash)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_memory(
    db: AsyncSession,
    memory_id: UUID,
    user_id: str,
    summary: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[list[str]] = None,
    embedding: Optional[list[float]] = None,
    status: Optional[str] = None,
) -> Optional[Memory]:
    """Update a memory record."""
    memory = await get_memory_by_id(db, memory_id, user_id)
    if not memory:
        return None

    if summary is not None:
        memory.summary = summary
    if category is not None:
        memory.category = category
    if tags is not None:
        memory.tags = tags
    if embedding is not None:
        memory.embedding = embedding
    if status is not None:
        memory.status = status

    await db.flush()
    await db.refresh(memory)
    return memory