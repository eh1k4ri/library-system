from fastapi import status
from app.core.errors import CustomError


class MissingCredentials(CustomError):
    def __init__(self):
        super().__init__(
            code="AUT001",
            title="Missing Credentials",
            description="Authorization header is required.",
            translation="Header de autorização é obrigatória.",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidCredentials(CustomError):
    def __init__(self):
        super().__init__(
            code="AUT002",
            title="Invalid Credentials",
            description="Invalid username or password.",
            translation="Usuário ou senha inválidos.",
            http_status=status.HTTP_401_UNAUTHORIZED,
        )
