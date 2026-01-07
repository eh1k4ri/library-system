from sqlalchemy import text
from sqlalchemy.orm import Session


class HealthcheckService:
    def check_system(self, db: Session):
        try:
            db.execute(text("SELECT 1"))
            return {
                "status": "available",
                "database": "connected",
                "message": "System is running",
            }
        except Exception as exc:
            return {
                "status": "unavailable",
                "database": "disconnected",
                "error": str(exc),
            }
