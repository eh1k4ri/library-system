import os
import base64
import secrets
from fastapi import Request, status
from starlette.responses import JSONResponse

SECURITY_USER = os.getenv("USER")
SECURITY_PASS = os.getenv("PASSWORD")


async def basic_auth(request: Request, call_next):
    public_paths = ["/docs", "/healthcheck", "/openapi.json"]

    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")

    def unauthorized_response(
        code: str, title: str, description: str, translation: str
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "detail": {
                    "code": code,
                    "title": title,
                    "description": description,
                    "translation": translation,
                }
            },
            headers={"WWW-Authenticate": "Basic realm=Library System"},
        )

    if not auth_header:
        return unauthorized_response(
            "AUTH_MISSING",
            "Missing Credentials",
            "Authorization header is required.",
            "Cabeçalho de autorização é obrigatório.",
        )

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
        return unauthorized_response(
            "AUTH_INVALID",
            "Invalid Credentials",
            "Invalid username or password.",
            "Usuário ou senha inválidos.",
        )

    response = await call_next(request)
    return response
