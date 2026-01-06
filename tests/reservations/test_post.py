from uuid import uuid4


def test_reservation_success(client):
    random_code = str(uuid4())[:8]
    email = f"reservation.{random_code}@test.com"

    user_payload = {"name": "Reservation Tester", "email": email}
    user_response = client.post("/users/", json=user_payload)
    assert user_response.status_code == 201, f"User failed: {user_response.json()}"
    user_key = user_response.json()["user_key"]

    book_payload = {"title": f"Reserved Book {random_code}", "author": "Tester Author"}
    book_response = client.post("/books/", json=book_payload)
    assert book_response.status_code == 201
    book_key = book_response.json()["book_key"]

    loan_payload = {"user_key": user_key, "book_key": book_key}
    loan_response = client.post("/loans/", json=loan_payload)
    assert loan_response.status_code == 201

    reservation_payload = {"user_key": user_key, "book_key": book_key}
    reservation_response = client.post("/reservations/", json=reservation_payload)

    assert reservation_response.status_code == 201
    data = reservation_response.json()
    assert data["status_name"] is not None
    assert data["book_title"] == book_payload["title"]
    assert data["user_name"] == user_payload["name"]
    assert data["expires_at"] is not None


def test_reservation_cannot_reserve_available_book(client):
    random_code = str(uuid4())[:8]
    email = f"avail.{random_code}@test.com"

    user_response = client.post("/users/", json={"name": "User", "email": email})
    user_key = user_response.json()["user_key"]

    book_response = client.post(
        "/books/", json={"title": f"Available Book {random_code}", "author": "Author"}
    )
    book_key = book_response.json()["book_key"]

    reservation_response = client.post(
        "/reservations/", json={"user_key": user_key, "book_key": book_key}
    )
    assert reservation_response.status_code == 400


def test_reservation_duplicate_active_reservation(client):
    random_code = str(uuid4())[:8]
    email = f"dup.{random_code}@test.com"

    user_response = client.post("/users/", json={"name": "User", "email": email})
    user_key = user_response.json()["user_key"]

    book_response = client.post(
        "/books/", json={"title": f"Book {random_code}", "author": "Author"}
    )
    book_key = book_response.json()["book_key"]

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

        res_response = client.post(
            "/reservations/", json={"user_key": user_key, "book_key": book_key}
        )
        assert res_response.status_code == 201
        reservations_created.append(res_response.json())

    assert len(reservations_created) == 2
