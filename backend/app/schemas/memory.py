from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional


class MemorySyncItem(BaseModel):
    local_image_id: str
    image_hash: str

    summary: str
    category: str
    tags: list[str]

    embedding: list[float]


class BatchSyncRequest(BaseModel):
    memories: list[MemorySyncItem]


class MemoryResponse(BaseModel):
    id: UUID

    local_image_id: str

    summary: Optional[str]  
    category: Optional[str]     
    tags: Optional[list[str]]

    status: str

    created_at: datetime

    model_config = {
        "from_attributes": True
    }