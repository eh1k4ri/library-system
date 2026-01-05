from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.healthcheck_service import HealthcheckService

router = APIRouter()
service = HealthcheckService()


@router.get("/", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    return service.check_system(db)
