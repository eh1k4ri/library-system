from typing import Optional, Union
from uuid import UUID


def validate_uuid(value: Union[str, UUID, None]) -> Optional[UUID]:
    if value is None:
        return None
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None
