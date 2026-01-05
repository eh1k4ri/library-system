def test_get_loans_list(client):
    user_response = client.post(
        "/users/", json={"name": "Test User", "email": "test@example.com"}
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

    response = client.get("/loans/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_loan_by_key(client):
    user_response = client.post(
        "/users/", json={"name": "Test User", "email": "test@example.com"}
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
    loan_key = loan_response.json()["loan_key"]

    response = client.get(f"/loans/{loan_key}")
    assert response.status_code == 200
    data = response.json()
    assert data["loan_key"] == loan_key
    assert data["status"]["enumerator"] == "active"


def test_get_loan_not_found(client):
    fake_key = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/loans/{fake_key}")
    assert response.status_code == 404
    assert "Loan not found" in response.json()["detail"]


def test_get_loans_pagination(client):
    user_response = client.post(
        "/users/", json={"name": "Test User", "email": "test@example.com"}
    )
    user_key = user_response.json()["user_key"]

    for i in range(5):
        book_response = client.post(
            "/books/", json={"title": f"Book {i}", "author": f"Author {i}"}
        )
        book_key = book_response.json()["book_key"]
        client.post("/loans/", json={"user_key": user_key, "book_key": book_key})

    response = client.get("/loans/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

    response = client.get("/loans/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2
