import json
import httpx

from app.core.config import settings
from app.services.vision.base import BaseVisionProvider


class OpenRouterVisionProvider(BaseVisionProvider):

    async def extract(
        self,
        image_base64: str,
        mime_type: str,
    ) -> dict:

        prompt = """
        Analyze this image and return ONLY JSON.

        {
          "summary": "short summary",
          "category": "travel/shopping/tech/etc",
          "tags": ["a", "b", "c"]
        }
        """

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
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{mime_type};base64,{image_base64}"
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                }
            )

        result = response.json()

        content = result["choices"][0]["message"]["content"]

        clean = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(clean)