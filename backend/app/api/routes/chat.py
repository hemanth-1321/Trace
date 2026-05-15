import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps.auth import CurrentUser, get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.services.vision.embeddings_service import get_embedding

router = APIRouter()


@router.post("")
async def chat(
    message: str,
    top_k: int = 3,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    query_embedding = await get_embedding(message)
    embedding_str = f"[{','.join(map(str, query_embedding))}]"

    result = await db.execute(
        text("""
            SELECT summary, category, tags
            FROM memories
            WHERE user_id = :user_id
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit
        """),
        {
            "user_id": current_user.user_id,
            "embedding": embedding_str,
            "limit": top_k,
        },
    )

    rows = result.fetchall()

    if not rows:
        context = "No relevant memories found."
    else:
        memories_text = "\n".join(
            f"- {r.summary} (category: {r.category}, tags: {r.tags})"
            for r in rows
        )
        context = f"Relevant memories:\n{memories_text}"

    system_prompt = (
        "You are a helpful assistant that answers questions based on the user's memories. "
        f"Use only the provided context. If unsure, say so.\n\n{context}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.VISION_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Chat response failed",
        )

    data = response.json()
    return {"response": data["choices"][0]["message"]["content"]}
