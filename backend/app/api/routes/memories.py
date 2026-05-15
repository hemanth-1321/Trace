from fastapi import APIRouter, Depends, HTTPException,status
from app.schemas.memory import BatchSyncRequest, MemoryResponse
from app.api.deps.auth import CurrentUser,get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.memory.memory_service import get_memory_by_hash, create_memory
router = APIRouter()


@router.post("/batch",response_model=list[MemoryResponse])
async def sync_batch(request: BatchSyncRequest,db: AsyncSession=Depends(get_db),current_user: CurrentUser=Depends(get_current_user)     ) -> list[MemoryResponse]:
    """Endpoint to sync a batch of memories from the client."""
    created=[]
    errors=[]
    for item in request.memories:
        existing=await get_memory_by_hash(db,current_user.user_id,item.image_hash)
        if existing:
            errors.append({
                "local_image_id": item.local_image_id,
                "error": "Memory with this image hash already exists."
            })
            continue
        try:
            memory=await create_memory(
                db=db,
                user_id=current_user.user_id,
                local_image_id=item.local_image_id,
                image_hash=item.image_hash,
                summary=item.summary,
                category=item.category,
                tags=item.tags,
                embedding=item.embedding
            )
            created.append(memory)
        except Exception as e:
            errors.append({
                "local_image_id": item.local_image_id,
                "error": str(e)
            })
    if errors and not created:
        # If all failed, return an error response
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"errors": errors})
    return [MemoryResponse.model_validate(memory) for memory in created]

    
