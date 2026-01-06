from sqlalchemy.orm import Session
from sqlalchemy import text


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
