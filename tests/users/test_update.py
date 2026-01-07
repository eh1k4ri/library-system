def test_update_user_success(client):
    response = client.post(
        "/users/", json={"name": "User One", "email": "one@test.com"}
    )
    assert response.status_code == 201
    user_key = response.json()["user_key"]

    update_response = client.patch(
        f"/users/{user_key}", json={"name": "User One Updated"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "User One Updated"


def test_update_user_conflict_email(client):
    client.post("/users/", json={"name": "A", "email": "a@test.com"})
    response_b = client.post("/users/", json={"name": "B", "email": "b@test.com"})
    user_key_b = response_b.json()["user_key"]

    update_response = client.patch(f"/users/{user_key_b}", json={"email": "a@test.com"})
    assert update_response.status_code == 400
    assert update_response.json()["detail"]["code"] == "LBS003"


def test_change_user_status(client):
    response = client.post("/users/", json={"name": "C", "email": "c@test.com"})
    user_key = response.json()["user_key"]

    update_status = client.post(
        f"/users/{user_key}/status", params={"status_enum": "suspended"}
    )
    assert update_status.status_code == 200
    assert update_status.json()["status"]["enumerator"] == "suspended"


def test_change_user_status_invalid(client):
    response = client.post("/users/", json={"name": "D", "email": "d@test.com"})
    user_key = response.json()["user_key"]

    update_status = client.post(
        f"/users/{user_key}/status", params={"status_enum": "unknown"}
    )
    assert update_status.status_code == 400
