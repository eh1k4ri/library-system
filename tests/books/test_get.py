import uuid


def test_get_books_list(client):
    client.post(
        "/books/", json={"title": "Book 1", "author": "Author 1", "genre": "Tech"}
    )
    client.post(
        "/books/", json={"title": "Book 2", "author": "Author 2", "genre": "Tech"}
    )

    response = client.get("/books/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_books_empty_list(client):
    response = client.get("/books/")

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_book_by_key(client, created_book):
    book_key = created_book["book_key"]
    response = client.get(f"/books/{book_key}")

    assert response.status_code == 200

    data = response.json()
    assert data["book_key"] == book_key
    assert data["title"] == created_book["title"]
    assert data["author"] == created_book["author"]


def test_get_book_not_found(client):
    fake_key = str(uuid.uuid4())
    response = client.get(f"/books/{fake_key}")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "LBS001"


def test_get_availability(client, created_book, created_user):
    book_key = created_book["book_key"]
    availability = client.get(f"/books/{book_key}/availability")
    assert availability.status_code == 200

    data = availability.json()
    assert data["available"] is True
    assert data["status"] == "available"

    user_key = created_user["user_key"]

    book_response = client.post(
        "/books/",
        json={"title": "Loaned Book", "author": "Author B", "genre": "History"},
    )
    assert book_response.status_code == 201
    loan_book_key = book_response.json()["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": loan_book_key}
    )
    assert loan_response.status_code == 201

    new_availability = client.get(f"/books/{loan_book_key}/availability")
    assert new_availability.status_code == 200
    data2 = new_availability.json()
    assert data2["available"] is False
    assert data2["status"] == "loaned"

    fake_key = str(uuid.uuid4())
    not_found_availability = client.get(f"/books/{fake_key}/availability")
    assert not_found_availability.status_code == 404
    assert not_found_availability.json()["detail"]["code"] == "LBS001"

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

    response = client.get("/books/?genre=Fantasy")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert all(book["genre"].lower() == "fantasy" for book in data)


def test_get_genres(client):
    client.post("/books/", json={"title": "G1", "author": "A1", "genre": "Drama"})
    client.post("/books/", json={"title": "G2", "author": "A2", "genre": "Horror"})

    response = client.get("/books/genres")
    assert response.status_code == 200
    genres = response.json()
    assert set([genre.lower() for genre in genres]).issuperset({"drama", "horror"})
