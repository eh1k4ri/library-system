def test_read_users_list(client):
    client.post("/users/", json={"name": "A", "email": "a@test.com"})
    client.post("/users/", json={"name": "B", "email": "b@test.com"})

    response = client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) >= 2
