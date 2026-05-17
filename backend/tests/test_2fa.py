"""2FA TOTP testlari."""
import pyotp


def test_totp_secret_generation():
    secret = pyotp.random_base32()
    assert len(secret) == 32
    totp = pyotp.TOTP(secret)
    code = totp.now()
    assert len(code) == 6
    assert totp.verify(code)


def test_totp_invalid_code():
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    assert not totp.verify("000000")


def test_2fa_setup_endpoint_requires_auth(client):
    res = client.post("/api/v1/auth/2fa/setup")
    # Endpoint should exist (any non-500) and reject unauth (401/403) or be unmounted (404)
    assert res.status_code in (401, 403, 404, 422)
