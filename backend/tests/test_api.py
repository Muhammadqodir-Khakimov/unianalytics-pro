"""API endpointlari integration testlari."""


def _login_as(client, username="admin"):
    """Helper — admin user yaratish va login qilish."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "email": f"{username}@test.com",
            "full_name": f"{username} test",
            "password": "secret123",
            "role": "admin",
        },
    )
    r = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "secret123"},
    )
    return r.json()["access_token"]


def test_olap_dimensions(client):
    token = _login_as(client)
    r = client.get("/api/v1/olap/dimensions", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    dims = r.json()
    assert len(dims) == 6
    names = {d["name"] for d in dims}
    assert "faculty" in names
    assert "time" in names


def test_olap_measures(client):
    token = _login_as(client)
    r = client.get("/api/v1/olap/measures", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    measures = r.json()
    assert any(m["name"] == "avg_grade" for m in measures)


def test_create_faculty_requires_admin(client):
    token = _login_as(client)
    r = client.post(
        "/api/v1/faculties",
        json={"name": "Test Fakultet", "code": "TST"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Test Fakultet"


def test_list_faculties(client):
    token = _login_as(client)
    client.post(
        "/api/v1/faculties",
        json={"name": "F1", "code": "F1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r = client.get("/api/v1/faculties", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
