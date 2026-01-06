def test_get_books_list(client):
    client.post(
        "/books/", json={"title": "Book 1", "author": "Author 1", "genre": "Tech"}
    )

    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_books_empty_list(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_book_by_key(client):
    create_response = client.post(
        "/books/",
        json={"title": "Python 101", "author": "John Doe", "genre": "Programming"},
    )
    assert create_response.status_code == 201
    book_key = create_response.json()["book_key"]

    response = client.get(f"/books/{book_key}")
    assert response.status_code == 200
    data = response.json()
    assert data["book_key"] == book_key
    assert data["title"] == "Python 101"
    assert data["author"] == "John Doe"


def test_get_book_not_found(client):
    fake_key = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/books/{fake_key}")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "LBS001"


def test_get_availability(client):
    resp = client.post(
        "/books/",
        json={"title": "Avail Book", "author": "Author A", "genre": "Fiction"},
    )
    assert resp.status_code == 201
    book_key = resp.json()["book_key"]

    a = client.get(f"/books/{book_key}/availability")
    assert a.status_code == 200
    data = a.json()
    assert data["available"] is True
    assert data["status"] == "available"

    user_resp = client.post(
        "/users/", json={"name": "Loan User", "email": "loanuser2@example.com"}
    )
    assert user_resp.status_code == 201
    user_key = user_resp.json()["user_key"]

    book_resp = client.post(
        "/books/",
        json={"title": "Loaned Book", "author": "Author B", "genre": "History"},
    )
    assert book_resp.status_code == 201
    loan_book_key = book_resp.json()["book_key"]

    loan_resp = client.post(
        "/loans/", json={"user_key": user_key, "book_key": loan_book_key}
    )
    assert loan_resp.status_code == 201

    a2 = client.get(f"/books/{loan_book_key}/availability")
    assert a2.status_code == 200
    data2 = a2.json()
    assert data2["available"] is False
    assert data2["status"] == "loaned"

    fake_key = "00000000-0000-0000-0000-000000000000"
    resp_nf = client.get(f"/books/{fake_key}/availability")
    assert resp_nf.status_code == 404
    assert resp_nf.json()["detail"]["code"] == "LBS001"

    response = client.get("/books/?page=2&per_page=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_get_books_filter_by_genre(client):
    client.post(
        "/books/", json={"title": "Genre A", "author": "Auth A", "genre": "Fantasy"}
    )
    client.post(
        "/books/", json={"title": "Genre B", "author": "Auth B", "genre": "Sci-Fi"}
    )

    r = client.get("/books/?genre=Fantasy")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert all(b["genre"].lower() == "fantasy" for b in data)


def test_get_genres(client):
    client.post("/books/", json={"title": "G1", "author": "A1", "genre": "Drama"})
    client.post("/books/", json={"title": "G2", "author": "A2", "genre": "Horror"})

    resp = client.get("/books/genres")
    assert resp.status_code == 200
    genres = resp.json()
    assert set([g.lower() for g in genres]).issuperset({"drama", "horror"})
