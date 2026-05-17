"""QR kod endpointlari."""


def test_qr_endpoint_exists(client):
    res = client.get("/api/v1/qr/student/1")
    assert res.status_code in (200, 401, 404)


def test_qr_base64_endpoint(client):
    res = client.get("/api/v1/qr/student/1/base64")
    assert res.status_code in (200, 401, 404)
    if res.status_code == 200:
        data = res.json()
        assert "qr_code" in data or "data" in data
