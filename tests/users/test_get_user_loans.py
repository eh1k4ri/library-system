def test_get_user_loans_empty(client):

    user_response = client.post(
        "/users/", json={"name": "Test User", "email": "test@example.com"}
    )
    user_key = user_response.json()["user_key"]

    response = client.get(f"/users/{user_key}/loans")
    assert response.status_code == 200
    assert response.json() == []


def test_get_user_with_loans(client):
    user_response = client.post(
        "/users/", json={"name": "Test User", "email": "test@example.com"}
    )
    user_key = user_response.json()["user_key"]

    book_response = client.post(
        "/books/", json={"title": "Test Book", "author": "Test Author"}
    )
    book_key = book_response.json()["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key, "days": 14}
    )
    assert loan_response.status_code == 201

    response = client.get(f"/users/{user_key}/loans")
    assert response.status_code == 200
    loans = response.json()
    assert len(loans) == 1
    assert loans[0]["status"]["enumerator"] == "active"


def test_get_user_loans_pagination(client):

    user_response = client.post(
        "/users/", json={"name": "Test User", "email": "test@example.com"}
    )
    user_key = user_response.json()["user_key"]

    for i in range(3):
        book_response = client.post(
            "/books/", json={"title": f"Book {i}", "author": f"Author {i}"}
        )
        book_key = book_response.json()["book_key"]
        client.post(
            "/loans/", json={"user_key": user_key, "book_key": book_key, "days": 14}
        )

    response = client.get(f"/users/{user_key}/loans?skip=0&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get(f"/users/{user_key}/loans?skip=1&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_user_loans_not_found(client):
    fake_key = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/users/{fake_key}/loans")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]
