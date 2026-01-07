def test_healthcheck(client):
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()

    assert data.get("status") == "available"
    assert data.get("database") == "connected"
    assert data.get("message") == "System is running"
