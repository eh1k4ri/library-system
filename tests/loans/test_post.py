from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app

client = TestClient(app)


def test_loan_sucess():
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

    return_payload = {"book_key": book_key}
    return_response = client.post("/loans/return", json=return_payload)

    assert return_response.status_code == 200
    return_data = return_response.json()
    assert return_data["status"]["enumerator"] == "returned"
    assert return_data["return_date"] is not None
    assert len(return_data["events"]) == 2


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
    assert "Book not found" in response.json()["detail"]


def test_loan_return_no_active_loan(client):
    book_response = client.post(
        "/books/", json={"title": "Test Book", "author": "Test Author"}
    )
    book_key = book_response.json()["book_key"]

    response = client.post("/loans/return", json={"book_key": book_key})
    assert response.status_code == 404
    assert "No active loan found" in response.json()["detail"]
