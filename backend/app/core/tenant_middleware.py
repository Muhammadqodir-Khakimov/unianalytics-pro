"""Tenant aniqlash middleware.

Tenant'ni quyidagi tartibda aniqlaydi:
1. `X-Tenant-Slug` header
2. Subdomain (acme.unianalytics.uz → "acme")
3. Token claim (`tenant_slug`)
4. Default (None — public DB)
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class TenantMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, base_domain: str = "unianalytics.uz"):
        super().__init__(app)
        self.base_domain = base_domain

    async def dispatch(self, request: Request, call_next):
        slug = self._resolve_slug(request)
        request.state.tenant_slug = slug
        return await call_next(request)

    def _resolve_slug(self, request: Request) -> str | None:
        header = request.headers.get("X-Tenant-Slug") or request.headers.get("X-Tenant-Subdomain")
        if header:
            return header.lower().strip()

        host = (request.headers.get("host") or "").split(":")[0]
        if host.endswith(f".{self.base_domain}"):
            sub = host[: -len(self.base_domain) - 1]
            if sub and sub not in ("www", "api", "docs"):
                return sub.lower()

        return None


def get_current_tenant(request: Request) -> str | None:
    """Dependency: hozirgi tenant slug'ini olish."""
    return getattr(request.state, "tenant_slug", None)
