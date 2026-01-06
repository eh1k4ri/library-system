import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str | None = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set via environment or .env")
SECURITY_USER: str = os.getenv("USER", "admin")
SECURITY_PASS: str = os.getenv("PASSWORD", "password123")

NOTIFY_WEBHOOK_URL: str | None = os.getenv("NOTIFY_WEBHOOK_URL")

LOAN_DEFAULT_DAYS: int = 14
LOAN_FINE_PER_DAY: float = 2.0
LOAN_MAX_ACTIVE_LOANS: int = 3
LOAN_RENEWAL_EXTENSION_DAYS: int = 7

RESERVATION_EXPIRY_DAYS: int = 7

CACHE_MAX_SIZE: int = 1000
CACHE_DEFAULT_TTL: int = 300
CACHE_ENTITY_TTL: int = 60
CACHE_STATUS_TTL: int = 300

RATE_LIMIT_REQUESTS: int = 100
RATE_LIMIT_WINDOW: int = 60
RATE_LIMIT_CLEANUP_INTERVAL: int = 600

PAGINATION_MIN: int = 100
PAGINATION_MAX_LIMIT: int = 1000
PAGINATION_DEFAULT_PAGE: int = 1

PUBLIC_PATHS: List[str] = [
    "/docs",
    "/openapi.json",
    "/healthcheck",
    "/metrics",
]

LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

APP_NAME: str = "Library System API"
