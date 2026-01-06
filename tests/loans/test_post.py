from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
from app.models.loan import Loan


def test_loan_sucess(client):
    random_code = str(uuid4())[:8]
    email = f"loan.{random_code}@test.com"

    user_payload = {"name": "Loan Tester", "email": email}
    user_response = client.post("/users/", json=user_payload)

    assert user_response.status_code == 201, f"User failed: {user_response.json()}"
    user_key = user_response.json()["user_key"]

    book_payload = {"title": f"Book {random_code}", "author": "Tester Author"}
    book_response = client.post("/books/", json=book_payload)
    assert book_response.status_code == 201
    book_key = book_response.json()["book_key"]

    loan_payload = {"user_key": user_key, "book_key": book_key}
    loan_response = client.post("/loans/", json=loan_payload)

    assert loan_response.status_code == 201
    data = loan_response.json()
    assert data["status"]["enumerator"] == "active"
    assert data["book"]["title"] == book_payload["title"]
    assert len(data["events"]) == 1

    fail_response = client.post("/loans/", json=loan_payload)
    assert fail_response.status_code == 400
    assert fail_response.json()["detail"]["code"] == "LBS004"

    return_payload = {"book_key": book_key}
    return_response = client.post("/loans/return", json=return_payload)

    assert return_response.status_code == 200
    return_data = return_response.json()
    assert return_data["status"]["enumerator"] == "returned"
    assert return_data["return_date"] is not None
    assert len(return_data["events"]) == 2


def test_loan_renew_success(client):
    random_code = str(uuid4())[:8]
    email = f"renew.{random_code}@test.com"

    user_resp = client.post("/users/", json={"name": "Renew User", "email": email})
    user_key = user_resp.json()["user_key"]

    book_resp = client.post(
        "/books/", json={"title": f"Renew Book {random_code}", "author": "Auth"}
    )
    book_key = book_resp.json()["book_key"]

    loan_resp = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    assert loan_resp.status_code == 201

    loan_data = loan_resp.json()
    old_due = datetime.fromisoformat(loan_data["due_date"])

    renew_resp = client.post(f"/loans/{loan_data['loan_key']}/renew")
    assert renew_resp.status_code == 200
    renewed = renew_resp.json()

    new_due = datetime.fromisoformat(renewed["due_date"])
    assert new_due > old_due
    assert renewed["status"]["enumerator"] == "active"
    assert len(renewed["events"]) == 2


def test_loan_renew_inactive(client):
    email = f"inactive.{str(uuid4())[:8]}@test.com"

    user_resp = client.post("/users/", json={"name": "Inactive Renew", "email": email})
    user_key = user_resp.json()["user_key"]

    book_resp = client.post(
        "/books/", json={"title": "Inactive Book", "author": "Auth"}
    )
    book_key = book_resp.json()["book_key"]

    loan_resp = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    loan_key = loan_resp.json()["loan_key"]

    client.post("/loans/return", json={"book_key": book_key})

    renew_resp = client.post(f"/loans/{loan_key}/renew")
    assert renew_resp.status_code == 400
    assert renew_resp.json()["detail"]["code"] == "LBS015"


def test_loan_renew_overdue(client, session):
    email = f"overdue.{str(uuid4())[:8]}@test.com"

    user_resp = client.post("/users/", json={"name": "Overdue Renew", "email": email})
    user_key = user_resp.json()["user_key"]

    book_resp = client.post("/books/", json={"title": "Overdue Book", "author": "Auth"})
    book_key = book_resp.json()["book_key"]

    loan_resp = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    loan_key = loan_resp.json()["loan_key"]

    loan_uuid = UUID(str(loan_key))
    loan = session.query(Loan).filter(Loan.loan_key == loan_uuid).first()
    loan.due_date = datetime.now(timezone.utc) - timedelta(days=3)
    session.commit()

    renew_resp = client.post(f"/loans/{loan_key}/renew")
    assert renew_resp.status_code == 400
    assert renew_resp.json()["detail"]["code"] == "LBS016"


def test_loan_return_success(client):
    user_response = client.post(
        "/users/", json={"name": "Test User", "email": "return.test@example.com"}
    )
    user_key = user_response.json()["user_key"]

    book_response = client.post(
        "/books/", json={"title": "Test Book", "author": "Test Author"}
    )
    book_key = book_response.json()["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    assert loan_response.status_code == 201

    return_response = client.post("/loans/return", json={"book_key": book_key})
    assert return_response.status_code == 200
    data = return_response.json()
    assert data["status"]["enumerator"] == "returned"
    assert data["return_date"] is not None


def test_loan_return_book_not_found(client):
    fake_key = "00000000-0000-0000-0000-000000000000"
    response = client.post("/loans/return", json={"book_key": fake_key})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "LBS001"


def test_loan_return_no_active_loan(client):
    book_response = client.post(
        "/books/", json={"title": "Test Book", "author": "Test Author"}
    )
    book_key = book_response.json()["book_key"]

    response = client.post("/loans/return", json={"book_key": book_key})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "LBS007"
