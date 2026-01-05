from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.loan_service import LoanService
from app.schemas.loan import LoanCreate, LoanResponse, LoanReturnRequest
from uuid import UUID

router = APIRouter()
service = LoanService()


@router.get("/", response_model=List[LoanResponse])
def read_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    loans = service.get_loans(db, skip=skip, limit=limit)
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
