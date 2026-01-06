from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.report_service import ReportService
from app.api.deps import PaginationParams

router = APIRouter()
report_service = ReportService()


@router.get("/reports/loans/export")
def export_loans(
    format: str = "csv",
    status_filter: Optional[str] = None,
    overdue: bool = False,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    try:
        content, media_type, filename = report_service.export_loans(
            db=db,
            skip=pagination.skip,
            limit=pagination.per_page,
            status_filter=status_filter,
            overdue=overdue,
            fmt=format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)


@router.get("/reports/users/export")
def export_users(
    format: str = "csv",
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    try:
        content, media_type, filename = report_service.export_users(
            db=db,
            skip=pagination.skip,
            limit=pagination.per_page,
            fmt=format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)


@router.get("/reports/books/export")
def export_books(
    format: str = "csv",
    genre: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    try:
        content, media_type, filename = report_service.export_books(
            db=db,
            skip=pagination.skip,
            limit=pagination.per_page,
            genre=genre,
            fmt=format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)


@router.get("/reports/reservations/export")
def export_reservations(
    format: str = "csv",
    user_key: Optional[str] = None,
    book_key: Optional[str] = None,
    status_filter: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    try:
        content, media_type, filename = report_service.export_reservations(
            db=db,
            skip=pagination.skip,
            limit=pagination.per_page,
            user_key=user_key,
            book_key=book_key,
            status_filter=status_filter,
            fmt=format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=content, media_type=media_type, headers=headers)
