from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_session
from app.services.loan_service import LoanService
from app.schemas.loan import LoanCreate, LoanResponse, LoanReturnRequest
from app.api.deps import PaginationParams
from app.core.errors import LoanNotFound

router = APIRouter()
service = LoanService()


@router.get("/", response_model=List[LoanResponse])
def get_loans(
    status: Optional[str] = None,
    overdue: bool = False,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
):
    loans = service.get_all(
        session,
        skip=pagination.skip,
        limit=pagination.per_page,
        status=status,
        overdue=overdue,
    )
    return loans


@router.get("/{loan_key}", response_model=LoanResponse)
def get_loan(loan_key: UUID, session: Session = Depends(get_session)):
    loan = service.get_by_key(session, loan_key=loan_key)
    if loan is None:
        raise LoanNotFound()
    return loan


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(loan_data: LoanCreate, session: Session = Depends(get_session)):
    return service.create(session=session, loan_data=loan_data)


@router.post("/return", response_model=LoanResponse)
def return_book(
    return_data: LoanReturnRequest, session: Session = Depends(get_session)
):
    return service.return_book(session=session, return_data=return_data)


@router.post("/{loan_key}/renew", response_model=LoanResponse)
def renew_loan(loan_key: UUID, session: Session = Depends(get_session)):
    return service.renew_loan(session=session, loan_key=loan_key)
