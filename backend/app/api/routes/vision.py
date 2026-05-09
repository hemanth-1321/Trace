from fastapi import APIRouter

router = APIRouter()


@router.post("/extract")
async def extract_vision() -> dict[str, str]:
    return {"status": "not_implemented"}