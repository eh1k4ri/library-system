def test_read_books_list(client):
    client.post("/books/", json={"title": "Book 1", "author": "Author 1"})

    response = client.get("/books/")
    assert response.status_code == 200
    assert len(response.json()) >= 1
