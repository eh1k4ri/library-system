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

    loan_payload = {"user_key": user_key, "book_key": book_key, "days": 7}
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
