"""Auth endpointlari uchun testlar."""


def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_login(client):
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "secret123",
    }
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 201
    assert r.json()["username"] == "testuser"

    # Login
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "secret123"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_register_duplicate_username(client):
    payload = {
        "username": "dup",
        "email": "dup1@example.com",
        "full_name": "Dup",
        "password": "secret123",
    }
    client.post("/api/v1/auth/register", json=payload)

    payload["email"] = "dup2@example.com"
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409


def test_login_invalid_credentials(client):
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "ghost", "password": "wrong"},
    )
    assert r.status_code == 401


def test_me_endpoint_requires_auth(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401
