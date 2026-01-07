def test_metrics(client):
    client.get("/healthcheck")
    client.get("/books")

    response = client.get("/metrics")
    assert response.status_code == 200

    body = response.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds_sum" in body
