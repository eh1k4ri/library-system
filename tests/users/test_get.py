import uuid


def test_get_users_list(client):
    client.post("/users/", json={"name": "A", "email": "a@test.com"})
    client.post("/users/", json={"name": "B", "email": "b@test.com"})

    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_users_empty_list(client):
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_by_key(client, created_user):
    user_key = created_user["user_key"]

    response = client.get(f"/users/{user_key}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_key"] == user_key
    assert data["name"] == created_user["name"]
    assert data["email"] == created_user["email"]


def test_get_user_not_found(client):
    fake_key = str(uuid.uuid4())
    response = client.get(f"/users/{fake_key}")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "LBS002"


def test_get_user_pagination(client):
    for i in range(5):
        client.post("/users/", json={"name": f"User {i}", "email": f"user{i}@test.com"})

    response = client.get("/users/?page=1&per_page=2")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = client.get("/users/?page=2&per_page=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
