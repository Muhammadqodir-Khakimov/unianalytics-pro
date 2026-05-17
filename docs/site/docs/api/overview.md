---
sidebar_position: 1
---

# API Reference

OpenAPI / Swagger UI: `https://your-backend/docs`
ReDoc: `https://your-backend/redoc`

## Auth

```http
POST /api/v1/auth/login
Content-Type: application/json

{ "username": "admin", "password": "admin123" }
```

Response:

```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

## Asosiy endpointlar

| Method | Path | Tavsif |
|--------|------|--------|
| GET | `/api/v1/students` | Talabalar ro'yxati |
| GET | `/api/v1/cube/query` | OLAP cube query |
| GET | `/api/v1/pivot` | Pivot tahlil |
| POST | `/api/v1/ml/predict-dropout` | Drop-out bashorat |
| GET | `/api/v1/cluster` | K-Means klasterlash |
| GET | `/api/v1/reports/dashboard` | Dashboard agregatlar |
| POST | `/api/v1/feedback/submit` | Anonim feedback |
| POST | `/api/v1/auth/2fa/setup` | 2FA o'rnatish |

## Rate limiting

100 req/min per IP, 1000 req/min per token (production).
