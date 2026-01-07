def test_update_book_success(client, created_book):
    book_key = created_book["book_key"]

    update_response = client.patch(
        f"/books/{book_key}", json={"title": "Book One Updated", "genre": "science"}
    )
    assert update_response.status_code == 200

    data = update_response.json()
    assert data["title"] == "Book One Updated"
    assert data["genre"] == "science"


def test_change_book_status(client, created_book):
    book_key = created_book["book_key"]

    update_response = client.post(
        f"/books/{book_key}/status", params={"status_enum": "loaned"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"]["enumerator"] == "loaned"


def test_change_book_status_invalid(client, created_book):
    book_key = created_book["book_key"]
    update_response = client.post(
        f"/books/{book_key}/status", params={"status_enum": "invalid"}
    )
    assert update_response.status_code == 400
