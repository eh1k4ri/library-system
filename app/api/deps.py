from fastapi import Query
from dataclasses import dataclass
from app.core.constants import PAGINATION_MIN, PAGINATION_MAX_LIMIT


@dataclass
class PaginationParams:
    page: int = Query(1, ge=1)
    per_page: int = Query(PAGINATION_MIN, ge=1, le=PAGINATION_MAX_LIMIT)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.per_page
