import pytest


def test_update_book_success(client):
    resp = client.post(
        "/books/",
        json={"title": "Book One", "author": "Author", "genre": "tech"},
    )
    assert resp.status_code == 201
    book_key = resp.json()["book_key"]

    upd = client.patch(
        f"/books/{book_key}", json={"title": "Book One Updated", "genre": "science"}
    )
    assert upd.status_code == 200
    body = upd.json()
    assert body["title"] == "Book One Updated"
    assert body["genre"] == "science"


def test_change_book_status(client):
    resp = client.post(
        "/books/",
        json={"title": "Book Two", "author": "Author", "genre": "tech"},
    )
    assert resp.status_code == 201
    book_key = resp.json()["book_key"]

    change = client.post(f"/books/{book_key}/status", params={"status_enum": "loaned"})
    assert change.status_code == 200
    assert change.json()["status"]["enumerator"] == "loaned"


def test_change_book_status_invalid(client):
    resp = client.post(
        "/books/",
        json={"title": "Book Three", "author": "Author", "genre": "tech"},
    )
    book_key = resp.json()["book_key"]

    change = client.post(f"/books/{book_key}/status", params={"status_enum": "invalid"})
    assert change.status_code == 400
