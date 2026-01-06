import os
import requests
from datetime import datetime
from typing import Optional
from app.core.logger import get_logger


class NotificationService:
    def __init__(self) -> None:
        self.webhook_url = os.getenv("NOTIFY_WEBHOOK_URL")
        self.logger = get_logger(__name__)

    def notify_due_date(
        self,
        *,
        user_email: str,
        loan_key: str,
        book_title: str,
        due_date: Optional[datetime]
    ) -> None:
        if not self.webhook_url:
            return

        payload = {
            "type": "loan_due_date",
            "loan_key": loan_key,
            "user_email": user_email,
            "book_title": book_title,
            "due_date": due_date.isoformat() if due_date else None,
        }

        try:
            resp = requests.post(self.webhook_url, json=payload, timeout=3)
            resp.raise_for_status()
        except Exception as exc:
            self.logger.warning("notification_failed", extra={"details": str(exc)})


notification_service = NotificationService()
