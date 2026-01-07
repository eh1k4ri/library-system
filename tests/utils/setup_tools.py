from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.models.loan import Loan


def create_loan(client, user_key: str, book_title: str, book_author: str):
    book_response = client.post(
        "/books/", json={"title": book_title, "author": book_author}
    )
    assert book_response.status_code == 201
    book_key = book_response.json()["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    assert loan_response.status_code == 201
    return loan_response.json(), book_key


def mark_loan_overdue(session, loan_key: str | UUID, days: int = 5):
    loan_key_uuid = UUID(str(loan_key))
    loan = session.query(Loan).filter(Loan.loan_key == loan_key_uuid).first()
    loan.due_date = datetime.now(timezone.utc) - timedelta(days=days)
    session.commit()


@pytest.fixture
def user_data():
    return {"name": "Test User", "email": "test@example.com"}


@pytest.fixture
def book_data():
    return {"title": "Test Book", "author": "Test Author"}


@pytest.fixture
def created_user(client, user_data):
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_book(client, book_data):
    response = client.post("/books/", json=book_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_loan(client, created_user, created_book):
    response = client.post(
        "/loans/",
        json={
            "user_key": created_user["user_key"],
            "book_key": created_book["book_key"],
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def created_reservation(client, created_user, created_book):
    loan_response = client.post(
        "/loans/",
        json={
            "user_key": created_user["user_key"],
            "book_key": created_book["book_key"],
        },
    )
    assert loan_response.status_code == 201

    response = client.post(
        "/reservations/",
        json={
            "user_key": created_user["user_key"],
            "book_key": created_book["book_key"],
        },
    )
    assert response.status_code == 201
    return response.json()
