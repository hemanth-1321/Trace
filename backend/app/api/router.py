from fastapi import APIRouter

from app.api.routes import auth, chat, memories, search, upload, vision

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(vision.router, prefix="/vision", tags=["vision"])
api_router.include_router(memories.router, prefix="/memories", tags=["memories"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])