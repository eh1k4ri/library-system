import csv
import io
from typing import Optional, Sequence, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy.orm import Session
from app.services.loan_service import LoanService
from app.services.user_service import UserService
from app.services.book_service import BookService
from app.services.reservation_service import ReservationService
from app.core.errors import InvalidExportFormat


class ReportService:
    def __init__(
        self,
        loan_service: Optional[LoanService] = None,
        user_service: Optional[UserService] = None,
        book_service: Optional[BookService] = None,
        reservation_service: Optional[ReservationService] = None,
    ) -> None:
        self.loan_service = loan_service or LoanService()
        self.user_service = user_service or UserService()
        self.book_service = book_service or BookService()
        self.reservation_service = reservation_service or ReservationService()

    @staticmethod
    def _validate_format(format: str) -> str:
        normalized_format = format.lower()
        if normalized_format not in {"csv", "pdf"}:
            raise InvalidExportFormat("Unsupported format. Use 'csv' or 'pdf'.")
        return normalized_format

    def _safe_get(self, obj: Any, path: str, default: str = "") -> str:
        current = obj
        for attr in path.split("."):
            if isinstance(current, dict):
                current = current.get(attr)
            else:
                current = getattr(current, attr, None)

            if current is None:
                return default

        return str(current)

    def _build_csv(
        self, headers: Sequence[str], rows: Sequence[Sequence[Any]]
    ) -> bytes:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)

        return output.getvalue().encode("utf-8")

    def _build_pdf(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
        title: str,
        subtitle: str,
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30,
        )
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(title, styles["Title"]))
        elements.append(Paragraph(subtitle, styles["Normal"]))
        elements.append(Spacer(1, 12))

        table_data = [headers] + [[str(col) for col in row] for row in rows]

        table = Table(table_data)

        style = TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
        table.setStyle(style)

        elements.append(table)

        doc.build(elements)
        return buffer.getvalue()

    def export_loans(
        self,
        session: Session,
        skip: int,
        limit: int,
        status_filter: Optional[str],
        overdue: bool,
        fmt: str,
    ) -> tuple[bytes, str, str]:
        normalized = self._validate_format(fmt)
        loans = self.loan_service.get_all(
            session,
            skip=skip,
            limit=limit,
            status=status_filter,
            overdue=overdue,
        )

        headers = [
            "Loan ID",
            "User ID",
            "Book ID",
            "Status",
            "Start",
            "Due",
            "Return",
            "Fine",
        ]

        rows = [
            [
                self._safe_get(loan, "loan_key"),
                self._safe_get(loan, "user_key"),
                self._safe_get(loan, "book_key"),
                self._safe_get(loan, "status.enumerator"),
                self._safe_get(loan, "start_date"),
                self._safe_get(loan, "due_date"),
                self._safe_get(loan, "return_date"),
                self._safe_get(loan, "fine_amount"),
            ]
            for loan in loans
        ]

        if normalized == "pdf":
            content = self._build_pdf(
                headers,
                rows,
                title="Loan Report",
                subtitle=f"Status: {status_filter or 'All'} | Overdue: {overdue}",
            )
            return content, "application/pdf", "loans.pdf"

        return self._build_csv(headers, rows), "text/csv", "loans.csv"

    def export_users(
        self, session: Session, skip: int, limit: int, fmt: str
    ) -> tuple[bytes, str, str]:
        normalized = self._validate_format(fmt)
        users = self.user_service.get_all(session, skip=skip, limit=limit)

        headers = ["User ID", "Name", "Email", "Status", "Created At"]

        rows = [
            [
                self._safe_get(user, "user_key"),
                self._safe_get(user, "name"),
                self._safe_get(user, "email"),
                self._safe_get(user, "status.enumerator"),
                self._safe_get(user, "created_at"),
            ]
            for user in users
        ]

        if normalized == "pdf":
            content = self._build_pdf(
                headers,
                rows,
                title="Users Report",
                subtitle="All users (paginated)",
            )
            return content, "application/pdf", "users.pdf"

        return self._build_csv(headers, rows), "text/csv", "users.csv"

    def export_books(
        self,
        session: Session,
        skip: int,
        limit: int,
        genre: Optional[str],
        fmt: str,
    ) -> tuple[bytes, str, str]:
        normalized = self._validate_format(fmt)
        books = self.book_service.get_all(
            session=session, skip=skip, limit=limit, genre=genre
        )

        headers = ["Book ID", "Title", "Author", "Genre", "Status", "Created At"]

        rows = [
            [
                self._safe_get(book, "book_key"),
                self._safe_get(book, "title"),
                self._safe_get(book, "author"),
                self._safe_get(book, "genre"),
                self._safe_get(book, "status.enumerator"),
                self._safe_get(book, "created_at"),
            ]
            for book in books
        ]

        subtitle = f"Genre: {genre}" if genre else "All genres"

        if normalized == "pdf":
            content = self._build_pdf(
                headers, rows, title="Books Report", subtitle=subtitle
            )
            return content, "application/pdf", "books.pdf"

        return self._build_csv(headers, rows), "text/csv", "books.csv"

    def export_reservations(
        self,
        session: Session,
        skip: int,
        limit: int,
        user_key: Optional[str],
        book_key: Optional[str],
        status_filter: Optional[str],
        fmt: str,
    ) -> tuple[bytes, str, str]:
        normalized = self._validate_format(fmt)
        reservations = self.reservation_service.get_all(
            session=session,
            skip=skip,
            limit=limit,
            user_key=user_key,
            book_key=book_key,
            status=status_filter,
        )

        headers = [
            "Res. ID",
            "User Name",
            "Book Title",
            "Status",
            "Reserved At",
            "Expires At",
            "Completed",
        ]

        rows = [
            [
                self._safe_get(reservation, "reservation_key"),
                self._safe_get(reservation, "user_name"),
                self._safe_get(reservation, "book_title"),
                self._safe_get(reservation, "status_name"),
                self._safe_get(reservation, "reserved_at"),
                self._safe_get(reservation, "expires_at"),
                self._safe_get(reservation, "completed_at"),
            ]
            for reservation in reservations
        ]

        subtitle = f"Status: {status_filter or 'any'}"

        if normalized == "pdf":
            content = self._build_pdf(
                headers, rows, title="Reservations Report", subtitle=subtitle
            )
            return content, "application/pdf", "reservations.pdf"

        return self._build_csv(headers, rows), "text/csv", "reservations.csv"
