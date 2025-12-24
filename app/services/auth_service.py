from sqlalchemy.orm import Session

from app.db.models import RefreshToken

# 세션 강제 종료 유틸
# 특정 유저의 refresh 토큰 전부 폐기
def revoke_all_refresh_tokens(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).update(
        {"revoked": True}, synchronize_session=False
    )
    db.commit()