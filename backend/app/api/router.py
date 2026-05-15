from fastapi import APIRouter,Depends

from app.api.routes import auth, chat, memories, search, vision

api_router = APIRouter()


api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
protected_router=APIRouter(dependencies=[Depends(auth.get_current_user)])

protected_router.include_router(vision.router, prefix="/vision", tags=["vision"])
protected_router.include_router(memories.router, prefix="/memories", tags=["memories"])
protected_router.include_router(search.router, prefix="/search", tags=["search"])
protected_router.include_router(chat.router, prefix="/chat", tags=["chat"])

api_router.include_router(protected_router)