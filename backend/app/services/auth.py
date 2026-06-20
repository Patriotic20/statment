from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models.user import User
from app.repositories.user import user_repo


async def authenticate(
    session: AsyncSession, username: str, password: str
) -> Optional[User]:
    """Return the user if the username exists and the password matches."""
    user = await user_repo.get_by_username(session, username)
    if user is None:
        return None
    if not verify_password(password, user.password):
        return None
    return user
