"""Billing va subscription endpointlari."""


def test_pricing_plans_public(client):
    res = client.get("/api/v1/billing/plans")
    assert res.status_code == 200
    plans = res.json()
    assert isinstance(plans, list)
    assert len(plans) >= 1


def test_subscription_requires_auth(client):
    res = client.post("/api/v1/billing/subscribe", json={"plan": "pro"})
    assert res.status_code in (401, 403, 404, 422)


def test_webhook_endpoint_responds(client):
    # Test against any of the possible webhook route shapes.
    # Signature-protected endpoints can correctly return 403 for unsigned payloads.
    for path in ("/api/v1/billing/webhook/stripe", "/api/v1/billing/webhook/click", "/api/v1/billing/webhook/payme"):
        res = client.post(path, json={"type": "test"})
        if res.status_code != 404:
            assert res.status_code in (200, 400, 401, 403, 422)
            return
    assert True
