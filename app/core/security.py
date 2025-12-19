from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import secrets
import hashlib

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def create_access_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    now = _now_utc()
    exp = now + timedelta(minutes=settings.access_token_expires_min)
    payload: Dict[str, Any] = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": secrets.token_urlsafe(16),
        "typ": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(subject: str) -> str:
    now = _now_utc()
    exp = now + timedelta(days=settings.refresh_token_expires_days)
    payload: Dict[str, Any] = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "jti": secrets.token_urlsafe(24),
        "typ": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> Dict[str, Any]:
    """
    Raises JWTError on invalid/expired token
    """
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer
    )

def refresh_cookie_params() -> Dict[str, Any]:
    # 개발환경에서만 secure=False 허용/ 운영에 붙일 경우 True.
    secure = settings.env != "dev"
    return {
        "httponly": True,
        "secure": secure,
        "samesite": "lax",
        "path": "/",
    }

def hash_refresh_token(token: str) -> str:
    """
    DB에 refresh token 원문 저장 금지. 추후 저장용 해시
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()