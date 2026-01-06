import csv
import io
from typing import Optional, Sequence
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session
from app.services.loan_service import LoanService
from app.services.user_service import UserService
from app.services.book_service import BookService
from app.services.reservation_service import ReservationService


class ReportService:
    def __init__(self) -> None:
        self.loan_service = LoanService()
        self.user_service = UserService()
        self.book_service = BookService()
        self.reservation_service = ReservationService()

    @staticmethod
    def _validate_format(fmt: str) -> str:
        normalized = fmt.lower()
        if normalized not in {"csv", "pdf"}:
            raise ValueError("Unsupported format. Use 'csv' or 'pdf'.")
        return normalized

    @staticmethod
    def _to_str(value):
        return "" if value is None else str(value)

    def _build_csv(
        self, headers: Sequence[str], rows: Sequence[Sequence[object]]
    ) -> bytes:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in rows:
            writer.writerow([self._to_str(col) for col in row])
        return output.getvalue().encode("utf-8")

    def _build_pdf(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[object]],
        title: str,
        subtitle: str,
    ) -> bytes:
        pdf_buffer = io.BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, height - 50, title)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(40, height - 65, subtitle)

        x_start = 40
        y = height - 90
        line_height = 14

        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawString(x_start, y, " | ".join(headers))
        pdf.setFont("Helvetica", 8)
        y -= line_height

        for row in rows:
            pdf.drawString(x_start, y, " | ".join([self._to_str(col) for col in row]))
            y -= line_height
            if y < 40:
                pdf.showPage()
                pdf.setFont("Helvetica", 8)
                y = height - 40

        pdf.save()
        return pdf_buffer.getvalue()

    def export_loans(
        self,
        db: Session,
        skip: int,
        limit: int,
        status_filter: Optional[str],
        overdue: bool,
        fmt: str,
    ) -> tuple[bytes, str, str]:
        normalized = self._validate_format(fmt)
        loans = self.loan_service.get_loans_filtered(
            db,
            skip=skip,
            limit=limit,
            status=status_filter,
            overdue=overdue,
        )

        headers_row = [
            "loan_key",
            "user_key",
            "book_key",
            "status",
            "start_date",
            "due_date",
            "return_date",
            "fine_amount",
        ]
        rows = [
            [
                getattr(loan, "loan_key", ""),
                getattr(loan, "user_key", ""),
                getattr(loan, "book_key", ""),
                getattr(getattr(loan, "status", None), "enumerator", ""),
                getattr(loan, "start_date", ""),
                getattr(loan, "due_date", ""),
                getattr(loan, "return_date", ""),
                getattr(loan, "fine_amount", ""),
            ]
            for loan in loans
        ]

        if normalized == "pdf":
            content = self._build_pdf(
                headers_row,
                rows,
                title="Loan Report",
                subtitle=f"Status: {status_filter or 'any'} | Overdue: {overdue}",
            )
            return content, "application/pdf", "loans.pdf"

        content = self._build_csv(headers_row, rows)
        return content, "text/csv", "loans.csv"

    def export_users(
        self, db: Session, skip: int, limit: int, fmt: str
    ) -> tuple[bytes, str, str]:
        normalized = self._validate_format(fmt)
        users = self.user_service.get_all(db, skip=skip, limit=limit)
        headers_row = ["user_key", "name", "email", "status", "created_at"]
        rows = [
            [
                getattr(u, "user_key", ""),
                getattr(u, "name", ""),
                getattr(u, "email", ""),
                getattr(getattr(u, "status", None), "enumerator", ""),
                getattr(u, "created_at", ""),
            ]
            for u in users
        ]

        if normalized == "pdf":
            content = self._build_pdf(
                headers_row,
                rows,
                title="Users Report",
                subtitle="All users (paginated)",
            )
            return content, "application/pdf", "users.pdf"

        content = self._build_csv(headers_row, rows)
        return content, "text/csv", "users.csv"

    def export_books(
        self,
        db: Session,
        skip: int,
        limit: int,
        genre: Optional[str],
        fmt: str,
    ) -> tuple[bytes, str, str]:
        normalized = self._validate_format(fmt)
        books = self.book_service.get_all(db=db, skip=skip, limit=limit, genre=genre)
        headers_row = ["book_key", "title", "author", "genre", "status", "created_at"]
        rows = [
            [
                getattr(b, "book_key", ""),
                getattr(b, "title", ""),
                getattr(b, "author", ""),
                getattr(b, "genre", ""),
                getattr(getattr(b, "status", None), "enumerator", ""),
                getattr(b, "created_at", ""),
            ]
            for b in books
        ]

        subtitle = f"Genre: {genre}" if genre else "All genres"

        if normalized == "pdf":
            content = self._build_pdf(
                headers_row, rows, title="Books Report", subtitle=subtitle
            )
            return content, "application/pdf", "books.pdf"

        content = self._build_csv(headers_row, rows)
        return content, "text/csv", "books.csv"

    def export_reservations(
        self,
        db: Session,
        skip: int,
        limit: int,
        user_key: Optional[str],
        book_key: Optional[str],
        status_filter: Optional[str],
        fmt: str,
    ) -> tuple[bytes, str, str]:
        normalized = self._validate_format(fmt)
        reservations = self.reservation_service.get_reservations(
            db=db,
            skip=skip,
            limit=limit,
            user_key=user_key,
            book_key=book_key,
            status=status_filter,
        )

        headers_row = [
            "reservation_key",
            "user_key",
            "user_name",
            "book_key",
            "book_title",
            "status",
            "reserved_at",
            "expires_at",
            "completed_at",
        ]
        rows = [
            [
                r.get("reservation_key"),
                r.get("user_key"),
                r.get("user_name"),
                r.get("book_key"),
                r.get("book_title"),
                r.get("status_name"),
                r.get("reserved_at"),
                r.get("expires_at"),
                r.get("completed_at"),
            ]
            for r in reservations
        ]

        subtitle = f"Status: {status_filter or 'any'}"

        if normalized == "pdf":
            content = self._build_pdf(
                headers_row, rows, title="Reservations Report", subtitle=subtitle
            )
            return content, "application/pdf", "reservations.pdf"

        content = self._build_csv(headers_row, rows)
        return content, "text/csv", "reservations.csv"
