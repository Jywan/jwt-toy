from fastapi import APIRouter, HTTPException, Response, Request, status
from pydantic import BaseModel, EmailStr

from jose import JWTError

from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    decode_token,
    refresh_cookie_params
)

router = APIRouter(prefix="/auth", tags=["auth"])

# 임시 유저 (DB 연동 이전 테스트용도)
_fake_user_db = {
    "jywan@test.com": {
        "id": "jywan",
        "email": "jywan@test.com",
        "password_hash": None,
    }
}

def _ensure_fake_user():
    u = _fake_user_db["jywan@test.com"]
    if u["password_hash"] is None:
        u["password_hash"] = hash_password("test")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response):
    _ensure_fake_user()
    user = _fake_user_db.get(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access = create_access_token(subject=user["id"])
    refresh = create_refresh_token(subject=user["id"])

    response.set_cookie(
        key="refresh_token",
        value=refresh,
        **refresh_cookie_params(),
    )

    return TokenResponse(access_token=access)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")
    
    try:
        claims = decode_token(refresh_token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    if claims.get("typ") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access = create_access_token(subject=user_id)
    new_refresh = create_refresh_token(subject=user_id)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        **refresh_cookie_params(),
    )
    
    return TokenResponse(access_token=new_access)

@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(key="refresh_token", path="/")
    return Response(status_code=204)