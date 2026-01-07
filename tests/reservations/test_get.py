import uuid


def test_get_reservations_list(client, created_reservation):
    response = client.get("/reservations/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_reservation_by_key(client, created_reservation):
    reservation_key = created_reservation["reservation_key"]
    response = client.get(f"/reservations/{reservation_key}")
    assert response.status_code == 200

    data = response.json()
    assert data["reservation_key"] == reservation_key
    assert data["completed_at"] is None


def test_get_reservation_not_found(client):
    fake_key = str(uuid.uuid4())
    response = client.get(f"/reservations/{fake_key}")
    assert response.status_code == 404


def test_get_reservations_filter_by_user(client, created_reservation, created_user):
    user_key = created_user["user_key"]
    response = client.get(f"/reservations/?user_key={user_key}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 1
    assert all(res["user"]["user_key"] == created_user["user_key"] for res in data)


def test_get_reservations_filter_by_book(client, created_reservation, created_book):
    book_key = created_book["book_key"]
    response = client.get(f"/reservations/?book_key={book_key}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(res["book"]["book_key"] == created_book["book_key"] for res in data)


def test_get_reservations_filter_by_status(client, created_reservation):
    response = client.get("/reservations/?status=ACTIVE")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_cancel_reservation(client, created_reservation):
    reservation_key = created_reservation["reservation_key"]

    response = client.delete(f"/reservations/{reservation_key}")
    assert response.status_code == 200
    data = response.json()
    assert data["reservation_key"] == reservation_key


def test_cancel_already_cancelled_reservation(client, created_reservation):
    reservation_key = created_reservation["reservation_key"]

    response1 = client.delete(f"/reservations/{reservation_key}")
    assert response1.status_code == 200

    response2 = client.delete(f"/reservations/{reservation_key}")
    assert response2.status_code == 400


def test_complete_reservation(client, created_reservation):
    reservation_key = created_reservation["reservation_key"]

    response = client.post(f"/reservations/{reservation_key}/complete")
    assert response.status_code == 200
    data = response.json()
    assert data["completed_at"] is not None


def test_complete_already_completed_reservation(client, created_reservation):
    reservation_key = created_reservation["reservation_key"]

    response1 = client.post(f"/reservations/{reservation_key}/complete")
    assert response1.status_code == 200

    response2 = client.post(f"/reservations/{reservation_key}/complete")
    assert response2.status_code == 400


def test_cannot_cancel_completed_reservation(client, created_reservation):
    reservation_key = created_reservation["reservation_key"]

    complete_response = client.post(f"/reservations/{reservation_key}/complete")
    assert complete_response.status_code == 200

    cancel_response = client.delete(f"/reservations/{reservation_key}")
    assert cancel_response.status_code == 400
