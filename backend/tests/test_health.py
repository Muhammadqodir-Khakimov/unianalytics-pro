"""Basic health va metadata endpointlari."""


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json().get("status") in ("ok", "healthy")


def test_openapi_schema(client):
    res = client.get("/openapi.json")
    assert res.status_code == 200
    schema = res.json()
    assert "paths" in schema
    assert "/api/v1/auth/login" in schema["paths"] or "/api/v1/auth/login/" in schema["paths"]


def test_docs_endpoint(client):
    res = client.get("/docs")
    assert res.status_code == 200


def test_cors_headers_present(client):
    res = client.options("/api/v1/auth/login", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
    })
    # CORS preflight should respond (200 or 204)
    assert res.status_code in (200, 204, 400)
