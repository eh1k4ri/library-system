from uuid import uuid4


def test_reservation_success(client, created_user, created_book):
    user_key = created_user["user_key"]
    book_key = created_book["book_key"]
    book_title = created_book["title"]
    user_name = created_user["name"]

    loan_payload = {"user_key": user_key, "book_key": book_key}
    loan_response = client.post("/loans/", json=loan_payload)
    assert loan_response.status_code == 201

    reservation_payload = {"user_key": user_key, "book_key": book_key}
    reservation_response = client.post("/reservations/", json=reservation_payload)

    assert reservation_response.status_code == 201

    data = reservation_response.json()
    assert data["status"]["enumerator"] is not None
    assert data["book"]["title"] == book_title
    assert data["user"]["name"] == user_name
    assert data["expires_at"] is not None


def test_reservation_cannot_reserve_available_book(client, created_user):
    user_key = created_user["user_key"]

    book_response = client.post(
        "/books/", json={"title": "Available Book", "author": "Author"}
    )
    book_key = book_response.json()["book_key"]

    reservation_response = client.post(
        "/reservations/", json={"user_key": user_key, "book_key": book_key}
    )
    assert reservation_response.status_code == 400


def test_reservation_duplicate_active_reservation(client, created_user, created_book):
    user_key = created_user["user_key"]
    book_key = created_book["book_key"]

    loan_response = client.post(
        "/loans/", json={"user_key": user_key, "book_key": book_key}
    )
    assert loan_response.status_code == 201

    first_reservation = client.post(
        "/reservations/", json={"user_key": user_key, "book_key": book_key}
    )
    assert first_reservation.status_code == 201

    second_reservation = client.post(
        "/reservations/", json={"user_key": user_key, "book_key": book_key}
    )
    assert second_reservation.status_code == 400


def test_reservation_multiple_different_books(client):
    random_code = str(uuid4())[:8]
    email = f"multi.{random_code}@test.com"

    user_response = client.post("/users/", json={"name": "User", "email": email})
    user_key = user_response.json()["user_key"]

    reservations_created = []
    for i in range(2):
        book_response = client.post(
            "/books/",
            json={"title": f"Book {random_code}-{i}", "author": f"Author {i}"},
        )
        book_key = book_response.json()["book_key"]

        other_user_response = client.post(
            "/users/",
            json={
                "name": f"Other User {i}",
                "email": f"other.{random_code}.{i}@test.com",
            },
        )
        other_user_key = other_user_response.json()["user_key"]
        client.post("/loans/", json={"user_key": other_user_key, "book_key": book_key})

        reservation_response = client.post(
            "/reservations/", json={"user_key": user_key, "book_key": book_key}
        )
        assert reservation_response.status_code == 201
        reservations_created.append(reservation_response.json())
    assert len(reservations_created) == 2
