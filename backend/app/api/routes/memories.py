from fastapi import APIRouter

router = APIRouter()


@router.post("/sync/batch")
async def sync_batch() -> dict[str, str]:
    return {"status": "not_implemented"}