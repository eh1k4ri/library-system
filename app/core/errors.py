from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class CustomError(HTTPException):
    code: str
    title: str
    description: str
    translation: str
    http_status: int

    def __init__(
        self,
        *,
        code: str,
        title: str,
        description: str,
        translation: str,
        http_status: int = status.HTTP_400_BAD_REQUEST,
        extra: Optional[Dict[str, Any]] = None,
    ):
        payload: Dict[str, Any] = {
            "code": code,
            "title": title,
            "description": description,
            "translation": translation,
        }
        if extra:
            payload.update(extra)

        super().__init__(status_code=http_status, detail=payload)
        self.code = code
        self.title = title
        self.description = description
        self.translation = translation
        self.http_status = http_status


class BookNotFound(CustomError):
    def __init__(self):
        super().__init__(
            code="LBS001",
            title="Book not found",
            description="Requested book was not found",
            translation="Livro não encontrado",
            http_status=status.HTTP_404_NOT_FOUND,
        )


class UserNotFound(CustomError):
    def __init__(self):
        super().__init__(
            code="LBS002",
            title="User not found",
            description="Requested user was not found",
            translation="Usuário não encontrado",
            http_status=status.HTTP_404_NOT_FOUND,
        )


class EmailAlreadyRegistered(CustomError):
    def __init__(self):
        super().__init__(
            code="LBS003",
            title="Email already registered",
            description="Email address already registered",
            translation="Email já registrado",
            http_status=status.HTTP_400_BAD_REQUEST,
        )


class BookNotAvailable(CustomError):
    def __init__(self):
        super().__init__(
            code="LBS004",
            title="Book is not available",
            description="Book is currently not available for loan",
            translation="Livro não está disponível",
            http_status=status.HTTP_400_BAD_REQUEST,
        )


class UserNotActive(CustomError):
    def __init__(self):
        super().__init__(
            code="LBS005",
            title="User is not active",
            description="User status is not active",
            translation="Usuário não está ativo",
            http_status=status.HTTP_400_BAD_REQUEST,
        )


class MaxActiveLoansReached(CustomError):
    def __init__(self):
        super().__init__(
            code="LBS006",
            title="User has reached maximum active loans",
            description="User reached the limit of active loans",
            translation="Usuário atingiu o máximo de empréstimos ativos",
            http_status=status.HTTP_400_BAD_REQUEST,
        )


class ActiveLoanNotFound(CustomError):
    def __init__(self):
        super().__init__(
            code="LBS007",
            title="No active loan found for this book",
            description="No active loan found for this book",
            translation="Nenhum empréstimo ativo encontrado para este livro",
            http_status=status.HTTP_404_NOT_FOUND,
        )


class LoanNotFound(CustomError):
    def __init__(self):
        super().__init__(
            code="LBS008",
            title="Loan not found",
            description="Requested loan was not found",
            translation="Empréstimo não encontrado",
            http_status=status.HTTP_404_NOT_FOUND,
        )


def http_error(
    error: CustomError, *, extra: Optional[Dict[str, Any]] = None
) -> CustomError:
    if extra:
        return CustomError(
            code=error.code,
            title=error.title,
            description=error.description,
            translation=error.translation,
            http_status=error.http_status,
            extra=extra,
        )
    return error
