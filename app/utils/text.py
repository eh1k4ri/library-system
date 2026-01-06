from typing import Optional


def normalize_email(value: str, field_name: str = "email") -> str:
    trimmed = clean_str(value, field_name)
    return trimmed.lower()


def clean_str(value: str, field_name: str = "value") -> str:
    if value is None:
        raise ValueError(f"{field_name} must not be null")
    trimmed = value.strip()
    if not trimmed:
        raise ValueError(f"{field_name} must not be empty or whitespace")
    return trimmed


def clean_optional_str(
    value: Optional[str], field_name: str = "value"
) -> Optional[str]:
    if value is None:
        return None
    return clean_str(value, field_name)
