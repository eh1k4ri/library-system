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


def test_get_user_by_key(client):
    create_response = client.post(
        "/users/", json={"name": "Test User", "email": "test@example.com"}
    )
    assert create_response.status_code == 201
    user_key = create_response.json()["user_key"]

    response = client.get(f"/users/{user_key}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_key"] == user_key
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"


def test_get_user_not_found(client):
    fake_key = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/users/{fake_key}")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_get_user_pagination(client):
    for i in range(5):
        client.post("/users/", json={"name": f"User {i}", "email": f"user{i}@test.com"})

    response = client.get("/users/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2

    response = client.get("/users/?skip=2&limit=2")
    assert response.status_code == 200
    assert len(response.json()) <= 2
