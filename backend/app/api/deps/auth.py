from functools import lru_cache
from typing import Any, Optional

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import PyJWKClient
from pydantic import BaseModel

from app.core.config import settings


class CurrentUser(BaseModel):
    user_id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@lru_cache
def get_jwk_client() -> PyJWKClient:
    jwks_url = f"{settings.CLERK_JWT_ISSUER}/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def _decode_token(token: str) -> dict[str, Any]:
    jwk_client = get_jwk_client()
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.CLERK_JWT_AUDIENCE,
        issuer=settings.CLERK_JWT_ISSUER,
    )


async def get_current_user(
    authorization: str = Header(..., alias="Authorization"),
) -> CurrentUser:
    """Extract and validate Clerk JWT from Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        claims = _decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return CurrentUser(
        user_id=claims["sub"],
        email=claims.get("email"),
        first_name=claims.get("given_name"),
        last_name=claims.get("family_name"),
    )
