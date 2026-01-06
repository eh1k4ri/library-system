from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from app.models.loan import Loan


def _mark_loan_overdue(session, loan_key: str | UUID, days: int = 5):
    loan_key_uuid = UUID(str(loan_key))
    loan = session.query(Loan).filter(Loan.loan_key == loan_key_uuid).first()
    assert loan is not None, "Loan not found when setting overdue"
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


def test_get_loans_list(client, created_loan):
    response = client.get("/loans/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_loan_by_key(client, created_loan):
    loan_key = created_loan["loan_key"]
    response = client.get(f"/loans/{loan_key}")
    assert response.status_code == 200
    data = response.json()
    assert data["loan_key"] == loan_key
    assert data["status"]["enumerator"] == "active"


def test_get_loan_not_found(client):
    fake_key = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/loans/{fake_key}")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "LBS008"


def test_get_loans_pagination(client, created_user):
    user_key = created_user["user_key"]
    for i in range(5):
        book_response = client.post(
            "/books/", json={"title": f"Book {i}", "author": f"Author {i}"}
        )
        book_key = book_response.json()["book_key"]
        client.post("/loans/", json={"user_key": user_key, "book_key": book_key})

    response = client.get("/loans/?page=1&per_page=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

    response = client.get("/loans/?page=2&per_page=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_get_loans_filter_status_and_overdue(client, session, created_user):
    user_key = created_user["user_key"]

    def create_loan(title, author):
        b_resp = client.post("/books/", json={"title": title, "author": author})
        b_key = b_resp.json()["book_key"]
        l_resp = client.post("/loans/", json={"user_key": user_key, "book_key": b_key})
        assert l_resp.status_code == 201
        return l_resp.json(), b_key

    loan1, _ = create_loan("Filter Book 1", "A")
    _, b2_key = create_loan("Filter Book 2", "B")

    ret = client.post("/loans/return", json={"book_key": b2_key})
    assert ret.status_code == 200

    r_active = client.get("/loans/?status=active")
    assert r_active.status_code == 200
    active_loans = r_active.json()
    assert any(l["loan_key"] == loan1["loan_key"] for l in active_loans)
    assert all(l["status"]["enumerator"] == "active" for l in active_loans)

    overdue_loan_data, b3_key = create_loan("Overdue Book", "C")

    _mark_loan_overdue(session, overdue_loan_data["loan_key"], days=5)

    r_overdue = client.get("/loans/?overdue=true")
    assert r_overdue.status_code == 200
    overdue_list = r_overdue.json()
    assert any(l["book"]["book_key"] == b3_key for l in overdue_list)
