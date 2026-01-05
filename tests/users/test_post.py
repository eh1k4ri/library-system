def test_create_user_success(client):
    response = client.post(
        "/users/", json={"name": "Tester User", "email": "create@test.com"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "create@test.com"


def test_create_user_duplicate_email(client):
    client.post("/users/", json={"name": "User 1", "email": "dup@test.com"})

    response = client.post("/users/", json={"name": "User 2", "email": "dup@test.com"})
    assert response.status_code == 400
