from fastapi import APIRouter, Depends

from app.api.deps.auth import CurrentUser, get_current_user

router = APIRouter()


@router.get("/me")
async def me(current_user: CurrentUser = Depends(get_current_user)) -> dict:
    """Get current user info from Clerk JWT."""
    return current_user.model_dump()
