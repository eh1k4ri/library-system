from sqlalchemy.orm import Session
from sqlalchemy import text


class HealthcheckService:
    def check_system(self, db: Session):

        try:
            db.execute(text("SELECT 1"))
            return {
                "status": "healthy",
                "database": "connected",
                "message": "System is running smoothly",
            }
        except Exception as e:
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
