import httpx

from app.core.config import settings

async def get_embedding(text: str) -> list[float]:  
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.OPENROUTER_BASE_URL}/embeddings",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.EMBEDDING_MODEL,
                "input": text
            }
        )

    result = response.json()
    return result["data"][0]["embedding"]