from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional
from app.models.role import RefreshToken


def create_refresh_token(db: Session, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
    rt = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()


def delete_refresh_token(db: Session, token: str) -> None:
    rt = get_refresh_token(db, token)
    if rt:
        db.delete(rt)
        db.commit()


def delete_user_tokens(db: Session, user_id: int) -> int:
    q = db.query(RefreshToken).filter(RefreshToken.user_id == user_id)
    count = q.count()
    q.delete(synchronize_session=False)
    db.commit()
    return count
