from fastapi import Query
from dataclasses import dataclass


@dataclass
class PaginationParams:
    page: int = Query(1, ge=1)
    per_page: int = Query(10, ge=1, le=100)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.per_page
