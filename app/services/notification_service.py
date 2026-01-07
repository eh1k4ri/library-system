from datetime import datetime
from typing import Optional

import requests

from app.core.constants import get_notify_webhook_url
from app.core.logger import get_logger


class NotificationService:
    def __init__(self) -> None:
        self.webhook_url = get_notify_webhook_url()
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
            response = requests.post(self.webhook_url, json=payload, timeout=3)
            response.raise_for_status()
        except Exception as exc:
            self.logger.warning("notification_failed", extra={"details": str(exc)})
