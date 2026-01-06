import base64
import secrets
from fastapi import Request
from app.core.constants import SECURITY_USER, SECURITY_PASS, PUBLIC_PATHS
from app.core.errors import MissingCredentials, InvalidCredentials


async def basic_auth(request: Request, call_next):
    if any(request.url.path.startswith(path) for path in PUBLIC_PATHS):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise MissingCredentials()

    try:
        scheme, credentials = auth_header.split(" ")
        if scheme.lower() != "basic":
            raise ValueError("Invalid scheme")

        decoded = base64.b64decode(credentials).decode("utf-8")
        username, password = decoded.split(":", 1)

        is_user_ok = secrets.compare_digest(username, SECURITY_USER)
        is_pass_ok = secrets.compare_digest(password, SECURITY_PASS)

        if not (is_user_ok and is_pass_ok):
            raise ValueError("Invalid credentials")

    except Exception:
        raise InvalidCredentials()

    response = await call_next(request)
    return response
