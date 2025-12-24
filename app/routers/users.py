from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.deps import get_db
from app.core.authz_deps import require_owner_or_admin, require_roles
from app.db.models import User
from app.routers.auth_service import revoke_all_refresh_token

router = APIRouter(prefix="/users", tags=["users"])

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None

class RoleUpdateRequest(BaseModel):
    role: str

@router.get("/{user_id}")
def get_user(user_id: int, _: User = Depends(require_owner_or_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        return {"detail": "Not found"}
    return {"id": u.id, "email": u.email, "role": u.role}

# 본인 프로필 수정 API
@router.patch("/{user_id}")
def update_user(user_id: int, payload: UserUpdateRequest, _: User = Depends(require_owner_or_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if payload.email is not None:
        # 중복 이메일 방지
        exists = db.query(User).filter(User.email == payload.email, User.id != user_id).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")
        u.email = payload.email

    db.commit()
    db.refresh(u)
    return {"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active}

# 관리자 전용: 권한 변경 API
@router.patch("/{user_id}/role")
def update_role(user_id: int, payload: RoleUpdateRequest, _: User = Depends(require_roles(["admin"])), db: Session = Depends(get_db)):
    if payload.role not in ("user", "admin"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Invalid role")
    
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    u.role = payload.role
    db.commit()
    db.refresh(u)
    return {"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active}

# 관지라 전용: 계정 비활성화 + 세션 강제종료 API
@router.patch("/{user_id}/disable")
def disable_user(user_id: int, _: User = Depends(require_roles(["admin"])), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    u.is_active = False
    db.commit()

    revoke_all_refresh_token(db, user_id)
    return {"id": u.id, "email": u.email, "role": u.role, "is_active": u.is_active}

# 관리자 전용: 유저 삭제
@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, _: User = Depends(require_roles(["admin"])), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.delete(u)
    db.commit()
    return