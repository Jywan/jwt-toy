from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.authz_deps import require_owner_or_admin
from app.db.models import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}")
def get_user(user_id: int, _: User = Depends(require_owner_or_admin), db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        return {"detail": "Not found"}
    return {"id": u.id, "email": u.email, "role": u.role}