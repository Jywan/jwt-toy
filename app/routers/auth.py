from datetime import datetime, timedelta, timezone
import secrets
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, Request, status, Depends
from pydantic import BaseModel, EmailStr
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.config import settings
from app.core.security import (
    verify_password, 
    create_access_token,
    create_refresh_token,
    decode_token,
    refresh_cookie_params,
    hash_refresh_token
)
from app.db.models import User, RefreshToken
from app.core.auth_deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _revoke_family(db: Session, family_id: str) -> None:
    db.query(RefreshToken).filter(RefreshToken.family_id == family_id).update(
        {"revoked": True}, synchronize_session=False
    )
    db.commit()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    
    user: Optional[User] = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access = create_access_token(subject=str(user.id), extra_claims={"role": user.role})
    refresh = create_refresh_token(subject=str(user.id))

    # DB 저장(원문 저장 금지 -> 해시화)
    family_id = secrets.token_hex(32)
    rt = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh),
        family_id=family_id,
        revoked=False,
        expires_at=_utcnow() + timedelta(days=settings.refresh_token_expires_days),
    )
    db.add(rt)
    db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh,
        **refresh_cookie_params(),
    )
    return TokenResponse(access_token=access)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    # 1) JWT 자체 검증
    try:
        claims = decode_token(refresh_token)
    except JWTError:
        response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if claims.get("typ") != "refresh":
        response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = claims.get("sub")
    if not user_id:
        response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # 2) DB에서 “해시”로 존재/폐기 여부 확인
    token_hash = hash_refresh_token(refresh_token)
    rt: Optional[RefreshToken] = (
        db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    )

    # DB에 없으면: 탈취/비정상 케이스로 보고 쿠키 제거 후 401
    if not rt:
        response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # 재사용 탐지: 이미 revoked 된 토큰을 들고 오면 family 전체 폐기
    if rt.revoked:
        _revoke_family(db, rt.family_id)
        response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token reuse detected")

    # 만료 시간(DB 기준)도 한 번 더 체크(방어적으로)
    if rt.expires_at <= _utcnow():
        rt.revoked = True
        db.commit()
        response.delete_cookie(key="refresh_token", path="/")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    # 3) Rotation: 기존 refresh 폐기 + 새 refresh 발급/저장
    rt.revoked = True
    rt.last_used_at = _utcnow()
    db.commit()

    new_access = create_access_token(subject=str(user_id))
    new_refresh = create_refresh_token(subject=str(user_id))

    new_rt = RefreshToken(
        user_id=int(user_id),
        token_hash=hash_refresh_token(new_refresh),
        family_id=rt.family_id,  # 같은 세션 체인 유지
        revoked=False,
        expires_at=_utcnow() + timedelta(days=settings.refresh_token_expires_days),
    )
    db.add(new_rt)
    db.commit()

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        **refresh_cookie_params(),
    )
    return TokenResponse(access_token=new_access)


@router.post("/logout", status_code=204)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        token_hash = hash_refresh_token(refresh_token)
        rt = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        if rt and not rt.revoked:
            rt.revoked = True
            db.commit()

    response.delete_cookie(key="refresh_token", path="/")
    return Response(status_code=204)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}