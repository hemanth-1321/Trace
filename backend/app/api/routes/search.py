from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.search import SearchRequest, SearchResultItem
from app.services.vision.embeddings_service import get_embedding

router = APIRouter()


@router.post("", response_model=list[SearchResultItem])
async def semantic_search(
    request: SearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SearchResultItem]:
    query_embedding = await get_embedding(request.query)
    embedding_str = f"[{','.join(map(str, query_embedding))}]"

    result = await db.execute(
        text("""
            SELECT
                id,
                local_image_id,
                summary,
                category,
                tags,
                1 - (embedding <=> :embedding::vector) AS score
            FROM memories
            WHERE user_id = :user_id
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """),
        {
            "user_id": current_user.user_id,
            "embedding": embedding_str,
            "limit": request.top_k,
        },
    )

    rows = result.fetchall()
    return [
        SearchResultItem(
            id=str(row.id),
            local_image_id=row.local_image_id,
            summary=row.summary,
            category=row.category,
            tags=row.tags,
            score=round(row.score, 4),
        )
        for row in rows
    ]
