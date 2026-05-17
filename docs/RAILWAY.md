# Railway deploy yo'riqnomasi

ReytingOLAP (SRAP-2026) ni Railway.com platformasida joylashtirish.

**Loyiha**: `a4e35fe2-62f0-4bd4-af50-2ac696da98f6`
**Asosiy URL**: https://railway.com/project/a4e35fe2-62f0-4bd4-af50-2ac696da98f6

---

## 1. Servislar tarkibi

Railway loyihasida 6 ta resurs bo'lishi shart:

| Servis | Tur | Manba | Vazifa |
|---|---|---|---|
| **postgres-oltp** | Plugin: PostgreSQL | Railway | Tranzaksion ma'lumotlar |
| **postgres-olap** | Plugin: PostgreSQL | Railway | DWH (star schema) |
| **redis** | Plugin: Redis | Railway | Kesh, Celery, bot FSM |
| **backend** | Web service | `./backend` | FastAPI API |
| **frontend** | Web service | `./frontend` | React SPA |
| **bot** | Worker (background) | `./apps/bot` | Telegram bot |

---

## 2. Tezkor deploy (CLI)

### 2.1. Talab qilinadigan dasturlar

```powershell
npm i -g @railway/cli           # CLI o'rnatish
railway --version               # >= 4.58
```

### 2.2. Autentifikatsiya va bog'lash

```powershell
railway login                                       # brauzerda OAuth
railway link a4e35fe2-62f0-4bd4-af50-2ac696da98f6   # loyihaga ulanish
```

### 2.3. Avtomatik deploy (1 buyruq)

```powershell
.\scripts\deploy_railway.ps1
```

Skript backend, frontend, bot servislariga ketma-ket deploy qiladi.

### 2.4. Qo'lda servisga deploy

```powershell
# Backend
railway up --service backend --detach

# Frontend
railway up --service frontend --detach

# Bot
railway up --service bot --detach
```

---

## 3. Environment variables (har bir servis uchun)

### Backend
| Variable | Manba | Tavsif |
|---|---|---|
| `APP_ENV` | `production` | Production rejim |
| `APP_DEBUG` | `false` | Debug o'chirilgan |
| `AUTO_INIT_DB` | `true` | Birinchi marta DB seedlash |
| `SECRET_KEY` | Auto-generate (32+ belgi) | JWT signature |
| `OLTP_DB_URL` | `${{Postgres-OLTP.DATABASE_URL}}` | OLTP ulanishi |
| `OLAP_DB_URL` | `${{Postgres-OLAP.DATABASE_URL}}` | OLAP ulanishi |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Kesh va Celery |
| `CORS_ORIGINS` | `https://<frontend>.up.railway.app` | CORS ruxsat |
| `SENTRY_DSN` | (ixtiyoriy) | Xato tracking |
| `ADMIN_PASSWORD` | (qattiq parol) | seed admin paroli |
| `DEKAN_PASSWORD` | (qattiq parol) | seed dekan paroli |
| `TEACHER_PASSWORD` | (qattiq parol) | seed o'qituvchi paroli |
| `STUDENT_PASSWORD` | (qattiq parol) | seed talaba paroli |

### Frontend
| Variable | Manba |
|---|---|
| `VITE_API_BASE_URL` | `https://<backend>.up.railway.app/api/v1` |
| `BACKEND_URL` | `https://<backend>.up.railway.app` (nginx proxy uchun) |

### Bot
| Variable | Manba |
|---|---|
| `TELEGRAM_BOT_TOKEN` | @BotFather dan olingan token |
| `BACKEND_API_URL` | `https://<backend>.up.railway.app/api/v1` |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` |
| `BOT_MODE` | `polling` (yoki `webhook` agar URL bo'lsa) |
| `WEBHOOK_URL` | (faqat webhook rejimi uchun) |
| `WEBHOOK_SECRET` | (faqat webhook rejimi uchun) |
| `RATE_LIMIT_PER_MIN` | `20` |

---

## 4. Migratsiyalar (deploy'dan keyin)

Birinchi deploy avtomatik `AUTO_INIT_DB=true` bilan `create_all()` qiladi va seed yuklaydi. Kelajakdagi migratsiyalarni qo'lda qo'llash:

```powershell
# OLTP head
railway run --service backend alembic -x target=oltp upgrade oltp@head

# OLAP head
railway run --service backend alembic -x target=olap upgrade olap@head

# Joriy holatni ko'rish
railway run --service backend alembic -x target=oltp current
railway run --service backend alembic -x target=olap current
```

Eski JSON saqlash bo'lsa, DB ga ko'chirish:

```powershell
railway run --service backend python -m scripts.migrate_parent_links_json_to_db
```

---

## 5. Healthcheck va monitoring

- Backend: `GET https://<backend>.up.railway.app/health` → `{"status": "ok"}`
- Prometheus metrikalar: `GET /metrics`
- Sentry: `SENTRY_DSN` o'rnatilgan bo'lsa avtomatik

Railway dashboard'da har bir servis uchun:
- **Logs** — real-time loglar
- **Metrics** — CPU, RAM, tarmoq
- **Deployments** — deploy tarixi va rollback

---

## 6. Bog'lanish daraxti

```
Telegram users
      ↓
   bot (polling)
      ↓ HTTPS /api/v1/*
   backend
      ↓                ↓                ↓
postgres-oltp    postgres-olap       redis
                                        ↑
                                     frontend (nginx proxy /api/)
                                        ↑
                                    Foydalanuvchilar
```

---

## 7. Tipik xatolar va yechimlar

| Xato | Yechim |
|---|---|
| Backend `Permission denied: /app/start.sh` | `chmod +x backend/start.sh` keyin commit |
| Frontend `${BACKEND_URL}` nginx'da | Railway `BACKEND_URL` variable o'rnatish, nginx envsubst ishlatish |
| Bot `TELEGRAM_BOT_TOKEN sozlanmagan` | Railway dashboard'da `sync: false` token kiritish |
| `psycopg2.OperationalError: SSL required` | URL avtomatik normalizatsiyasi (config.py) — qayta deploy |
| Multi-head alembic | `alembic upgrade head` o'rniga `alembic upgrade oltp@head` |
| Bot xabar yuborolmaydi | Bot SAME loyihada bo'lishi va REDIS_URL to'g'ri ekanligi tekshirish |

---

## 8. Foydali buyruqlar

```powershell
railway status                          # joriy loyiha holati
railway logs --service backend          # real-time loglar
railway logs --service bot --tail 200
railway run --service backend bash      # konteyner ichida shell
railway variables --service backend     # env variablelarni ko'rish
railway domain                          # public URL olish
```
