def test_health(client):
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_rejects_post(client):
    response = client.post("/api/v1/health/")
    assert response.status_code == 405


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "SMS Guard" in response.content.decode("utf-8")
