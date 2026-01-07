import uuid
from tests.utils.setup_tools import create_loan, mark_loan_overdue


def test_get_loans_list(client):
    response = client.get("/loans/")

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_loan_by_key(client, created_loan):
    loan_key = created_loan["loan_key"]
    response = client.get(f"/loans/{loan_key}")

    assert response.status_code == 200

    data = response.json()
    assert data["loan_key"] == loan_key
    assert data["status"]["enumerator"] == "active"


def test_get_loan_not_found(client):
    fake_key = str(uuid.uuid4())
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
    assert len(response.json()) == 2

    response = client.get("/loans/?page=2&per_page=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_get_loans_filter_status_and_overdue(client, session, created_user):
    user_key = created_user["user_key"]

    loan_response_1, book1_key = create_loan(client, user_key, "Filter Book 1", "A")
    loan_response_2, book2_key = create_loan(client, user_key, "Filter Book 2", "B")

    return_response = client.post("/loans/return", json={"book_key": book2_key})
    assert return_response.status_code == 200

    reponse_active = client.get("/loans/?status=active")
    assert reponse_active.status_code == 200
    active_loans = reponse_active.json()
    assert any(loan["loan_key"] == loan_response_1["loan_key"] for loan in active_loans)
    assert all(loan["status"]["enumerator"] == "active" for loan in active_loans)

    overdue_loan_data, book3_key = create_loan(client, user_key, "Overdue Book", "C")

    mark_loan_overdue(session, overdue_loan_data["loan_key"], days=5)

    reponse_overdue = client.get("/loans/?overdue=true")
    assert reponse_overdue.status_code == 200
    overdue_list = reponse_overdue.json()
    assert any(loan["book"]["book_key"] == book3_key for loan in overdue_list)
