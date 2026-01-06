from sqlalchemy.orm import Session
from app.models.user import User
from app.models.loan import Loan
from app.models.user_status import UserStatus
from app.schemas.user import UserCreate
from app.core.errors import EmailAlreadyRegistered, UserNotFound
from app.utils.uuid import validate_uuid


class UserService:
    def create(self, db: Session, user: UserCreate):
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise EmailAlreadyRegistered()

        active_status = (
            db.query(UserStatus).filter(UserStatus.enumerator == "active").first()
        )

        new_user = User(name=user.name, email=user.email, status_id=active_status.id)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(User).offset(skip).limit(limit).all()

    def get_by_key(self, db: Session, user_key: str):
        user_key = validate_uuid(user_key)
        if not user_key:
            return None
        return db.query(User).filter(User.user_key == user_key).first()

    def get_user_loans(
        self, db: Session, user_key: str, skip: int = 0, limit: int = 100
    ):
        user_key = validate_uuid(user_key)
        if not user_key:
            return None

        user = db.query(User).filter(User.user_key == user_key).first()
        if not user:
            raise UserNotFound()

        return (
            db.query(Loan)
            .filter(Loan.user_id == user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
