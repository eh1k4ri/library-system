import uuid


def test_get_user_loans_empty(client, created_user):
    user_key = created_user["user_key"]

    response = client.get(f"/users/{user_key}/loans")
    assert response.status_code == 200
    assert response.json() == []


def test_get_user_with_loans(client, created_user, created_book):
    user_key = created_user["user_key"]
    book_key = created_book["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    assert loan_response.status_code == 201

    response = client.get(f"/users/{user_key}/loans")
    assert response.status_code == 200

    loans = response.json()
    assert len(loans) == 1
    assert loans[0]["status"]["enumerator"] == "active"


def test_get_user_loans_pagination(client, created_user):
    user_key = created_user["user_key"]

    for i in range(3):
        book_response = client.post(
            "/books/", json={"title": f"Book {i}", "author": f"Author {i}"}
        )
        book_key = book_response.json()["book_key"]
        client.post("/loans/", json={"user_key": user_key, "book_key": book_key})

    response = client.get(f"/users/{user_key}/loans?page=1&per_page=1")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(f"/users/{user_key}/loans?page=2&per_page=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user_loans_not_found(client):
    fake_key = str(uuid.uuid4())
    response = client.get(f"/users/{fake_key}/loans")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "LBS002"
