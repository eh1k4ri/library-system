def test_create_book_success(client):
    response = client.post(
        "/books/", json={"title": "Clean Code", "author": "Uncle Bob"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Clean Code"
    assert data["status"]["enumerator"] == "available"
