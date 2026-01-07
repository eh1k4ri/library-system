def test_post_user_success(client):
    response = client.post(
        "/users/", json={"name": "Tester User", "email": "create@test.com"}
    )
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "create@test.com"
    assert data["name"] == "Tester User"
    assert data["status"]["enumerator"] == "active"
    assert "user_key" in data


def test_post_user_duplicate_email(client):
    client.post("/users/", json={"name": "User 1", "email": "dup@test.com"})

    response = client.post("/users/", json={"name": "User 2", "email": "dup@test.com"})

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "LBS003"


def test_post_user_with_valid_data(client):
    response = client.post(
        "/users/", json={"name": "Jane Smith", "email": "jane.smith@example.com"}
    )
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Jane Smith"
    assert data["email"] == "jane.smith@example.com"


def test_post_multiple_users(client):
    emails = ["user1@test.com", "user2@test.com", "user3@test.com"]
    created_users = []

    for email in emails:
        response = client.post(
            "/users/", json={"name": f"User {email}", "email": email}
        )
        assert response.status_code == 201
        created_users.append(response.json())

    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) >= 3
