from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResultItem(BaseModel):
    id: str
    local_image_id: str
    summary: Optional[str]
    category: Optional[str]
    tags: Optional[list[str]]
    score: float