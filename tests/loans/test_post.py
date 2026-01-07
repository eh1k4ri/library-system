import uuid
from datetime import datetime
from tests.utils.setup_tools import mark_loan_overdue


def test_loan_sucess(client, created_user, created_book):
    user_key = created_user["user_key"]
    book_key = created_book["book_key"]
    book_title = created_book["title"]

    loan_payload = {"user_key": user_key, "book_key": book_key}
    loan_response = client.post("/loans/", json=loan_payload)

    assert loan_response.status_code == 201
    data = loan_response.json()
    assert data["status"]["enumerator"] == "active"
    assert data["book"]["title"] == book_title
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


def test_loan_renew_success(client, created_user, created_book):
    user_key = created_user["user_key"]
    book_key = created_book["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    assert loan_response.status_code == 201

    loan_data = loan_response.json()
    old_due = datetime.fromisoformat(loan_data["due_date"])

    renew_response = client.post(f"/loans/{loan_data['loan_key']}/renew")
    assert renew_response.status_code == 200
    renewed = renew_response.json()

    new_due = datetime.fromisoformat(renewed["due_date"])
    assert new_due > old_due
    assert renewed["status"]["enumerator"] == "active"
    assert len(renewed["events"]) == 2


def test_loan_renew_inactive(client, created_user, created_book):
    user_key = created_user["user_key"]
    book_key = created_book["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    loan_key = loan_response.json()["loan_key"]

    client.post("/loans/return", json={"book_key": book_key})

    renew_response = client.post(f"/loans/{loan_key}/renew")
    assert renew_response.status_code == 400
    assert renew_response.json()["detail"]["code"] == "LBS015"


def test_loan_renew_overdue(client, session, created_user, created_book):
    user_key = created_user["user_key"]
    book_key = created_book["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    loan_key = loan_response.json()["loan_key"]

    mark_loan_overdue(session, loan_key, days=3)

    renew_response = client.post(f"/loans/{loan_key}/renew")
    assert renew_response.status_code == 400
    assert renew_response.json()["detail"]["code"] == "LBS016"


def test_loan_return_success(client, created_user, created_book):
    user_key = created_user["user_key"]
    book_key = created_book["book_key"]

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
    fake_key = str(uuid.uuid4())
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
