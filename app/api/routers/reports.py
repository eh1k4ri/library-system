from typing import Optional
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.db.session import get_session
from app.services.report_service import ReportService
from app.api.deps import PaginationParams
from app.core.errors import InvalidExportFormat

router = APIRouter()
report_service = ReportService()


@router.get("/report/loans/export")
def export_loans(
    format: str = "csv",
    status_filter: Optional[str] = None,
    overdue: bool = False,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
):
    try:
        content, media_type, filename = report_service.export_loans(
            session=session,
            skip=pagination.skip,
            limit=pagination.per_page,
            status_filter=status_filter,
            overdue=overdue,
            fmt=format,
        )
    except ValueError as exc:
        raise InvalidExportFormat(str(exc))

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)


@router.get("/report/users/export")
def export_users(
    format: str = "csv",
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
):
    try:
        content, media_type, filename = report_service.export_users(
            session=session,
            skip=pagination.skip,
            limit=pagination.per_page,
            fmt=format,
        )
    except ValueError as exc:
        raise InvalidExportFormat(str(exc))

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)


@router.get("/report/books/export")
def export_books(
    format: str = "csv",
    genre: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
):
    try:
        content, media_type, filename = report_service.export_books(
            session=session,
            skip=pagination.skip,
            limit=pagination.per_page,
            genre=genre,
            fmt=format,
        )
    except ValueError as exc:
        raise InvalidExportFormat(str(exc))

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)


@router.get("/report/reservations/export")
def export_reservations(
    format: str = "csv",
    user_key: Optional[str] = None,
    book_key: Optional[str] = None,
    status_filter: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
):
    try:
        content, media_type, filename = report_service.export_reservations(
            session=session,
            skip=pagination.skip,
            limit=pagination.per_page,
            user_key=user_key,
            book_key=book_key,
            status_filter=status_filter,
            fmt=format,
        )
    except ValueError as exc:
        raise InvalidExportFormat(str(exc))

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)
