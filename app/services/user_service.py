from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.loan import Loan
from app.models.user_status import UserStatus
from app.schemas.user import UserCreate, UserUpdate
from app.core.errors import EmailAlreadyRegistered, UserNotFound
from app.utils.uuid import validate_uuid
from app.utils.cache import get_cache, set_cache


class UserService:
    def create(self, session: Session, user: UserCreate):
        existing_user = session.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise EmailAlreadyRegistered()

        active_status = (
            session.query(UserStatus).filter(UserStatus.enumerator == "active").first()
        )

        new_user = User(name=user.name, email=user.email, status_id=active_status.id)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    def get_all(self, session: Session, skip: int = 0, limit: int = 100):
        return (
            session.query(User)
            .options(joinedload(User.status))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_key(self, session: Session, user_key: str):
        user_key = validate_uuid(user_key)
        if not user_key:
            return None

        cache_key = f"user:{user_key}:details"
        cached_data = get_cache(cache_key)
        if cached_data:
            return cached_data

        user = (
            session.query(User)
            .options(joinedload(User.status))
            .filter(User.user_key == user_key)
            .first()
        )

        if user:
            set_cache(cache_key, user, ttl_seconds=60)

        return user

    def update(self, session: Session, user_key: str, data: UserUpdate):
        user = self.get_by_key(session, user_key)
        if not user:
            raise UserNotFound()

        if data.email and data.email != user.email:
            existing = session.query(User).filter(User.email == data.email).first()
            if existing and existing.id != user.id:
                raise EmailAlreadyRegistered()

        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            user.email = data.email

        session.commit()
        session.refresh(user)
        set_cache(f"user:{user_key}:details", user, ttl_seconds=60)
        return user

    def set_status(self, session: Session, user_key: str, status_enum: str):
        user = self.get_by_key(session, user_key)
        if not user:
            raise UserNotFound()

        status = (
            session.query(UserStatus)
            .filter(UserStatus.enumerator == status_enum)
            .first()
        )
        if not status:
            raise ValueError(f"Invalid status: {status_enum}")

        user.status_id = status.id
        session.commit()
        session.refresh(user)
        set_cache(f"user:{user_key}:details", user, ttl_seconds=60)
        return user

    def get_user_loans(
        self, session: Session, user_key: str, skip: int = 0, limit: int = 100
    ):
        user = self.get_by_key(session, user_key)

        if not user:
            raise UserNotFound()

        return (
            session.query(Loan)
            .options(joinedload(Loan.book), joinedload(Loan.status))
            .filter(Loan.user_id == user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )
