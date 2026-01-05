def test_get_books_list(client):
    client.post("/books/", json={"title": "Book 1", "author": "Author 1"})

    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_books_empty_list(client):
    response = client.get("/books/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_book_by_key(client):
    create_response = client.post(
        "/books/", json={"title": "Python 101", "author": "John Doe"}
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
    assert "Book not found" in response.json()["detail"]


def test_get_books_pagination(client):
    for i in range(5):
        client.post("/books/", json={"title": f"Book {i}", "author": f"Author {i}"})

    response = client.get("/books/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

    response = client.get("/books/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2
