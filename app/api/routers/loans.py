from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.loan_service import LoanService
from app.schemas.loan import LoanCreate, LoanResponse, LoanReturnRequest
from uuid import UUID

router = APIRouter()
service = LoanService()


@router.get("/", response_model=List[LoanResponse])
def read_loans(
    page: int = 1,
    per_page: int = 100,
    status: Optional[str] = None,
    overdue: bool = False,
    db: Session = Depends(get_db),
):
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if per_page < 1:
        raise HTTPException(status_code=400, detail="per_page must be >= 1")
    loans = service.get_loans_filtered(
        db, page=page, per_page=per_page, status=status, overdue=overdue
    )
    return loans


@router.get("/{loan_key}", response_model=LoanResponse)
def read_loan(loan_key: UUID, db: Session = Depends(get_db)):
    loan = service.get_loan_by_key(db, loan_key=loan_key)
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(loan_data: LoanCreate, db: Session = Depends(get_db)):
    return service.create_loan(db=db, loan_data=loan_data)


@router.post("/return", response_model=LoanResponse)
def return_book(return_data: LoanReturnRequest, db: Session = Depends(get_db)):
    return service.return_book(db=db, return_data=return_data)
