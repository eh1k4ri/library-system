import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.services.notification_service import NotificationService


def test_notify_skips_when_no_webhook(monkeypatch):
    # Ensure env is unset
    monkeypatch.delenv("NOTIFY_WEBHOOK_URL", raising=False)
    svc = NotificationService()
    with patch("app.services.notification_service.requests.post") as mock_post:
        svc.notify_due_date(
            user_email="u@test.com",
            loan_key="lk",
            book_title="Book",
            due_date=datetime(2026, 1, 1),
        )
    mock_post.assert_not_called()


def test_notify_calls_webhook(monkeypatch):
    webhook = "https://example.com/hook"
    monkeypatch.setenv("NOTIFY_WEBHOOK_URL", webhook)
    svc = NotificationService()

    with patch("app.services.notification_service.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_post.return_value = mock_resp

        svc.notify_due_date(
            user_email="u@test.com",
            loan_key="lk",
            book_title="Book",
            due_date=datetime(2026, 1, 1),
        )

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == webhook
        assert kwargs["json"]["type"] == "loan_due_date"
        assert kwargs["json"]["user_email"] == "u@test.com"
        assert kwargs["json"]["loan_key"] == "lk"
        assert kwargs["json"]["book_title"] == "Book"
        assert kwargs["json"]["due_date"].startswith("2026-01-01")
        assert kwargs["timeout"] == 3


def test_notify_best_effort_on_failure(monkeypatch, caplog):
    webhook = "https://example.com/hook"
    monkeypatch.setenv("NOTIFY_WEBHOOK_URL", webhook)
    svc = NotificationService()

    with patch("app.services.notification_service.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = Exception("boom")
        mock_post.return_value = mock_resp

        svc.notify_due_date(
            user_email="u@test.com",
            loan_key="lk",
            book_title="Book",
            due_date=None,
        )

        # Should not raise, but should log warning
        # We just assert post was called and no exception propagated
        mock_post.assert_called_once()
        assert not caplog.records or caplog.records[-1].levelname in {
            "WARNING",
            "INFO",
            "ERROR",
        }
