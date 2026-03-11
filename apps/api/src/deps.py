"""FastAPI dependencies: auth (JWT), optional DB session."""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_async_session
from models.user import User


async def get_token_from_authorization(
    authorization: Annotated[str | None, Header()] = None,
) -> str | None:
    """Extract Bearer token from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization.removeprefix("Bearer ").strip() or None


async def get_current_user_optional(
    token: Annotated[str | None, Depends(get_token_from_authorization)] = None,
    session: Annotated[AsyncSession, Depends(get_async_session)] = None,
) -> User | None:
    """
    Resolve current user from JWT if present. Returns None when no/invalid token.
    """
    if not token:
        return None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        external_id: str | None = payload.get("sub")
        if not external_id:
            return None
    except JWTError:
        return None
    result = await session.execute(select(User).where(User.external_id == external_id))
    user = result.scalar_one_or_none()
    return user


async def get_current_user(
    user: Annotated[User | None, Depends(get_current_user_optional)] = None,
) -> User:
    """Require authenticated user. Raise 401 if missing."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
