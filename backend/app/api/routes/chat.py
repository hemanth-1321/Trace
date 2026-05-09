from fastapi import APIRouter

router = APIRouter()


@router.post("")
async def chat() -> dict[str, str]:
    return {"status": "not_implemented"}