from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def semantic_search() -> dict[str, str]:
    return {"status": "not_implemented"}