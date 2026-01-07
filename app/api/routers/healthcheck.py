from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.services.healthcheck_service import HealthcheckService

router = APIRouter()
service = HealthcheckService()


@router.get("/", tags=["System"])
def health_check(session: Session = Depends(get_session)):
    return service.check_system(session)
