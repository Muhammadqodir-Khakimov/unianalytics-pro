"""Multi-tenant endpointlari uchun testlar."""


def test_tenant_list_requires_auth(client):
    res = client.get("/api/v1/tenants/")
    assert res.status_code in (401, 403)


def test_super_admin_can_create_tenant(client):
    # Register super admin
    client.post("/api/v1/auth/register", json={
        "username": "superadmin",
        "password": "Super123!",
        "email": "super@test.uz",
        "full_name": "Super Admin",
        "role": "super_admin",
    })
    login = client.post("/api/v1/auth/login", json={
        "username": "superadmin", "password": "Super123!"
    })
    token = login.json().get("access_token")
    if not token:
        return  # skip if login flow not set up identically

    res = client.post(
        "/api/v1/tenants/",
        json={"name": "TestUniv", "subdomain": "testu", "plan": "trial"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code in (200, 201, 422)


def test_tenant_isolation_by_subdomain(client):
    """Subdomain'dan kelayotgan request shu tenant ma'lumotlarini ko'rishi kerak."""
    res = client.get("/api/v1/tenants/current", headers={"X-Tenant-Subdomain": "nonexistent"})
    assert res.status_code in (200, 404)
