import csv
import io


def test_export_loans_csv(client, created_loan):
    response = client.get("/reports/loans/export?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "loans.csv" in response.headers.get("content-disposition", "")

    rows = list(csv.reader(io.StringIO(response.text)))
    assert len(rows) == 2


def test_export_loans_pdf(client, created_loan):
    response = client.get("/reports/loans/export?format=pdf")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "loans.pdf" in response.headers.get("content-disposition", "")
    assert len(response.content) >= 1


def test_export_users_csv(client, created_user):
    response = client.get("/reports/users/export?format=csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "users.csv" in response.headers.get("content-disposition", "")
    assert created_user["email"] in response.text


def test_export_books_pdf(client):
    response_create = client.post(
        "/books/",
        json={"title": "Book C", "author": "Author", "genre": "fiction"},
    )
    assert response_create.status_code == 201

    response = client.get("/reports/books/export?format=pdf&genre=fiction")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "books.pdf" in response.headers.get("content-disposition", "")
    assert len(response.content) >= 1


def test_export_reservations_csv(client, created_reservation):
    response = client.get("/reports/reservations/export?format=csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "reservations.csv" in response.headers.get("content-disposition", "")
    rows = list(csv.reader(io.StringIO(response.text)))
    assert len(rows) == 2


def test_export_invalid_format(client):
    response = client.get("/reports/loans/export?format=xml")
    assert response.json()["detail"]["code"] == "LBS018"
