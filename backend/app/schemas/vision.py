from pydantic import BaseModel

class VisionRequest(BaseModel):
    image_base64: str
    mime_type: str
    image_hash: str

class VisionResponse(BaseModel):
    summary: str
    category: str
    tags: list[str]
    embedding: list[float]

