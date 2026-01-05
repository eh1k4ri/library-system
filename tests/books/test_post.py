def test_post_book_success(client):
    response = client.post(
        "/books/", json={"title": "Clean Code", "author": "Uncle Bob"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Clean Code"
    assert data["author"] == "Uncle Bob"
    assert data["status"]["enumerator"] == "available"
    assert "book_key" in data


def test_post_multiple_books(client):
    books = [
        {"title": "Book 1", "author": "Author 1"},
        {"title": "Book 2", "author": "Author 2"},
        {"title": "Book 3", "author": "Author 3"},
    ]
    created_books = []

    for book in books:
        response = client.post("/books/", json=book)
        assert response.status_code == 201
        created_books.append(response.json())

    response = client.get("/books/")
    assert len(response.json()) >= 3


def test_post_book_with_same_title_different_author(client):
    book = {"title": "Python Guide", "author": "Author 1"}
    response1 = client.post("/books/", json=book)
    assert response1.status_code == 201

    book["author"] = "Author 2"
    response2 = client.post("/books/", json=book)
    assert response2.status_code == 201

    assert response1.json()["book_key"] != response2.json()["book_key"]
