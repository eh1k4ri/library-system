import logging
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key in [
            "operation",
            "entity_type",
            "entity_id",
            "user_id",
            "status",
            "trace_id",
            "path",
            "method",
            "status_code",
            "duration_ms",
        ]:
            if hasattr(record, key):
                data[key] = getattr(record, key)

        if hasattr(record, "details") and record.details is not None:
            data["details"] = record.details

        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)

        return json.dumps(data, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    env_level = os.getenv("LOG_LEVEL")
    level = env_level or level

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if root_logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)

    logging.getLogger("sqlalchemy.engine").setLevel("WARNING")
    logging.getLogger("urllib3").setLevel("WARNING")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_operation(
    logger: logging.Logger,
    *,
    operation: str,
    entity_type: str,
    status: str = "success",
    entity_id: Optional[str] = None,
    user_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
    level: str = "info",
) -> None:
    log_fn = getattr(logger, level.lower(), logger.info)
    log_fn(
        f"{operation} {entity_type}",
        extra={
            "operation": operation,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "status": status,
            "details": details,
            "trace_id": trace_id,
        },
    )
