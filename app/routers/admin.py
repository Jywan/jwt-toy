from fastapi import APIRouter, Depends

from app.core.authz_deps import require_roles
from app.db.models import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/ping")
def admin_ping(user: User = Depends(require_roles(["admin"]))):
    return {"ok": True, "admin": user.email}