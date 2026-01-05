from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.user_status import UserStatus
from app.schemas.user import UserCreate


class UserService:
    def create(self, db: Session, user: UserCreate):
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        active_status = (
            db.query(UserStatus).filter(UserStatus.enumerator == "active").first()
        )
        if not active_status:
            raise HTTPException(status_code=500, detail="Status 'active' not found")

        new_user = User(name=user.name, email=user.email, status_id=active_status.id)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()
