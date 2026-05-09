from fastapi import APIRouter, File, UploadFile

router = APIRouter()


@router.post("")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    return {"filename": file.filename or ""}