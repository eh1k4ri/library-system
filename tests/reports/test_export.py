import base64
import csv
import io


def _create_user(client, name: str, email: str) -> str:
    resp = client.post("/users/", json={"name": name, "email": email})
    assert resp.status_code == 201
    return resp.json()["user_key"]


def _create_book(client, title: str, author: str, genre: str = "test") -> str:
    resp = client.post(
        "/books/",
        json={"title": title, "author": author, "genre": genre},
    )
    assert resp.status_code == 201
    return resp.json()["book_key"]


def _create_loan(client, user_key: str, book_key: str) -> str:
    resp = client.post("/loans/", json={"user_key": user_key, "book_key": book_key})
    assert resp.status_code == 201
    return resp.json()["loan_key"]


def _create_reservation(client, user_key: str, book_key: str):
    resp = client.post(
        "/reservations/",
        json={"user_key": user_key, "book_key": book_key},
    )
    assert resp.status_code == 201
    return resp.json()["reservation_key"]


def test_export_loans_csv(client):
    user_key = _create_user(client, "User A", "a@test.com")
    book_key = _create_book(client, "Book A", "Author")
    _create_loan(client, user_key, book_key)

    resp = client.get("/reports/loans/export?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "loans.csv" in resp.headers.get("content-disposition", "")

    rows = list(csv.reader(io.StringIO(resp.text)))
    assert len(rows) >= 2  # header + at least one row


def test_export_loans_pdf(client):
    user_key = _create_user(client, "User B", "b@test.com")
    book_key = _create_book(client, "Book B", "Author")
    _create_loan(client, user_key, book_key)

    resp = client.get("/reports/loans/export?format=pdf")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/pdf")
    assert "loans.pdf" in resp.headers.get("content-disposition", "")
    assert len(resp.content) > 0


def test_export_users_csv(client):
    _create_user(client, "User C", "c@test.com")

    resp = client.get("/reports/users/export?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "users.csv" in resp.headers.get("content-disposition", "")
    assert "c@test.com" in resp.text


def test_export_books_pdf(client):
    _create_book(client, "Book C", "Author", genre="fiction")

    resp = client.get("/reports/books/export?format=pdf&genre=fiction")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/pdf")
    assert "books.pdf" in resp.headers.get("content-disposition", "")
    assert len(resp.content) > 0


def test_export_reservations_csv(client):
    # Need a loan to make the book unavailable, then create reservation
    user1 = _create_user(client, "User D", "d@test.com")
    user2 = _create_user(client, "User E", "e@test.com")
    book_key = _create_book(client, "Book D", "Author")
    _create_loan(client, user1, book_key)
    _create_reservation(client, user2, book_key)

    resp = client.get("/reports/reservations/export?format=csv")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "reservations.csv" in resp.headers.get("content-disposition", "")
    rows = list(csv.reader(io.StringIO(resp.text)))
    assert len(rows) >= 2


def test_export_invalid_format_returns_400(client):
    resp = client.get("/reports/loans/export?format=xml")
    assert resp.status_code == 400
    assert "Unsupported format" in resp.json()["detail"]
