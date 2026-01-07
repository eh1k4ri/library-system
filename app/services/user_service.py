from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.loan import Loan
from app.models.user_status import UserStatus
from app.models.user_event import UserEvent
from app.schemas.user import UserCreate, UserUpdate
from app.core.constants import CACHE_ENTITY_TTL
from app.core.errors import EmailAlreadyRegistered, UserNotFound
from app.utils.uuid import validate_uuid
from app.utils.cache import get_cache, set_cache, clear_cache


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
        session.flush()

        self._create_event(session, new_user.id, None, active_status.id)

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
        cached_user = get_cache(cache_key)
        if cached_user:
            return cached_user

        user = (
            session.query(User)
            .options(joinedload(User.status))
            .filter(User.user_key == user_key)
            .first()
        )

        if user:
            set_cache(cache_key, user, ttl_seconds=CACHE_ENTITY_TTL)

        return user

    def _get_for_update(self, session: Session, user_key: str) -> User | None:
        uuid = validate_uuid(user_key)
        if not uuid:
            return None

        return session.query(User).filter(User.user_key == uuid).first()

    def update(self, session: Session, user_key: str, data: UserUpdate):
        user = self._get_for_update(session, user_key)

        if not user:
            return None

        if data.name is not None:
            user.name = data.name
        if data.email is not None:
            existing = session.query(User).filter(User.email == data.email).first()
            if existing and existing.id != user.id:
                raise EmailAlreadyRegistered()
            user.email = data.email

        session.commit()
        session.refresh(user)

        set_cache(f"user:{user_key}:details", user, ttl_seconds=CACHE_ENTITY_TTL)

        return user

    def set_status(self, session: Session, user_key: str, status_enum: str):
        user = self._get_for_update(session, user_key)
        if not user:
            return None

        status = (
            session.query(UserStatus)
            .filter(UserStatus.enumerator == status_enum)
            .first()
        )
        if not status:
            return None

        old_status_id = user.status_id
        user.status_id = status.id

        self._create_event(session, user.id, old_status_id, status.id)

        session.commit()
        session.refresh(user)

        clear_cache(f"user:{user_key}:details")

        return user

    def _create_event(
        self,
        session: Session,
        user_id: int,
        old_status_id: Optional[int],
        new_status_id: int,
    ):
        event = UserEvent(
            user_id=user_id,
            old_status_id=old_status_id,
            new_status_id=new_status_id,
            created_at=datetime.now(),
        )
        session.add(event)

    def get_user_loans(
        self,
        session: Session,
        user_key: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ):
        user = self.get_by_key(session, user_key)

        if not user:
            raise UserNotFound()

        query = (
            session.query(Loan)
            .options(joinedload(Loan.book), joinedload(Loan.status))
            .filter(Loan.user_id == user.id)
        )

        if status:
            query = query.join(Loan.status).filter(Loan.status.has(enumerator=status))

        return query.offset(skip).limit(limit).all()
