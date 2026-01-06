from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.loan import Loan
from app.models.user_status import UserStatus
from app.schemas.user import UserCreate
from app.core.errors import EmailAlreadyRegistered, UserNotFound
from app.utils.uuid import validate_uuid
from app.utils.cache import get_cache, set_cache


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
        return (
            db.query(User)
            .options(joinedload(User.status))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_key(self, db: Session, user_key: str):
        user_key = validate_uuid(user_key)
        if not user_key:
            return None

        cache_key = f"user:{user_key}:data"
        cached_data = get_cache(cache_key)
        if cached_data:
            return cached_data

        user = (
            db.query(User)
            .options(joinedload(User.status))
            .filter(User.user_key == user_key)
            .first()
        )

        if user:
            set_cache(cache_key, user, ttl_seconds=60)

        return user

    def get_user_loans(
        self, db: Session, user_key: str, skip: int = 0, limit: int = 100
    ):
        user = self.get_by_key(db, user_key)

        if not user:
            raise UserNotFound()

        return (
            db.query(Loan)
            .options(joinedload(Loan.book), joinedload(Loan.status))
            .filter(Loan.user_id == user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
