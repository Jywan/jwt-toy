from typing import Callable, Iterable
from fastapi import Depends, HTTPException, status

from app.core.auth_deps import get_current_user
from app.db.models import User

# 인가 Dependency
def require_roles(allowed: Iterable[str]) -> Callable:
    allowed_set = set(allowed)

    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_set:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden",)
        return user
    return _dep


def require_owner_or_admin(user_id: int, user: User = Depends(get_current_user)) -> User:
    if user.role == "admin":
        return user
    
    if user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden",)
    return user