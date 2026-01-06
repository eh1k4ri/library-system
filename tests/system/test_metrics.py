def test_metrics_endpoint(client):
    # Trigger a couple of requests to generate metrics
    client.get("/healthcheck")
    client.get("/books")

    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds_sum" in body