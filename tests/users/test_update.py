import pytest


def test_update_user_success(client):
    resp = client.post("/users/", json={"name": "User One", "email": "one@test.com"})
    assert resp.status_code == 201
    user_key = resp.json()["user_key"]

    upd = client.patch(f"/users/{user_key}", json={"name": "User One Updated"})
    assert upd.status_code == 200
    assert upd.json()["name"] == "User One Updated"


def test_update_user_conflict_email(client):
    # Create two users
    client.post("/users/", json={"name": "A", "email": "a@test.com"})
    resp_b = client.post("/users/", json={"name": "B", "email": "b@test.com"})
    user_key_b = resp_b.json()["user_key"]

    upd = client.patch(f"/users/{user_key_b}", json={"email": "a@test.com"})
    assert upd.status_code == 400
    assert upd.json()["detail"]["code"] == "LBS001"


def test_change_user_status(client):
    resp = client.post("/users/", json={"name": "C", "email": "c@test.com"})
    user_key = resp.json()["user_key"]

    change = client.post(
        f"/users/{user_key}/status", params={"status_enum": "suspended"}
    )
    assert change.status_code == 200
    assert change.json()["status"]["enumerator"] == "suspended"


def test_change_user_status_invalid(client):
    resp = client.post("/users/", json={"name": "D", "email": "d@test.com"})
    user_key = resp.json()["user_key"]

    change = client.post(f"/users/{user_key}/status", params={"status_enum": "unknown"})
    assert change.status_code == 400
