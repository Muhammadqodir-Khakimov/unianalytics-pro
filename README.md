# ReytingOLAP — Student Rating Analytics Platform

**Talabalar reytingini OLAP tahlili asosida monitoring qilish axborot tizimi (SRAP-2026)**

Bitiruv malakaviy ishi (BMI) doirasida ishlab chiqilgan ko'p platformali korporativ analitik tizim. O'zDSt 34.602-2018 standartiga muvofiq.

**Ilmiy rahbar:** Onarkulov Maksadjon Karimberdiyevich

---

## Loyiha haqida

Tizim **OLAP (Online Analytical Processing)** modeliga asoslangan bo'lib, talabalar reyting ma'lumotlarini ko'p o'lchovli kub (cube) ko'rinishida tahlil qilish va 6 xil foydalanuvchi guruhiga (rektorat, dekan, kafedra, o'qituvchi, talaba, ota-ona) zarur axborotni qulay platformalar orqali yetkazib berish imkonini beradi.

**OLAP operatsiyalari:**
- **Drill-down / Roll-up** — Universitet ↔ Fakultet ↔ Kafedra ↔ Guruh ↔ Talaba
- **Slice / Dice** — bir yoki bir nechta o'lchov bo'yicha filtrlash
- **Pivot** — o'lchovlarni almashtirish
- **Drill-through** — agregatdan birlamchi yozuvlarga o'tish
- **CUBE / ROLLUP / GROUPING SETS** — SQL darajasida agregatsiya

## Tizim komponentlari

| Komponent | Texnologiya | Maqsad |
|---|---|---|
| **Backend API** | Python 3.11 + FastAPI | OLAP, ETL, ML, REST API |
| **OLAP DWH** | PostgreSQL 15+, Star Schema | 1 fakt + **7 dimension** + materialized views |
| **OLTP** | PostgreSQL 15+ | Tranzaksion ma'lumotlar |
| **Web ilova** | React 18 + TypeScript + Vite + Ant Design | Rahbariyat / analitika markazi |
| **Mobil ilova** | Flutter 3.16+ (Dart 3) | Talaba va o'qituvchi shaxsiy kabineti |
| **Telegram bot** | Python aiogram 3 | Tezkor kirish, ota-ona kanali |
| **ETL** | Celery + Redis | HEMIS → DWH avtomatik sinxronizatsiya |
| **ML** | scikit-learn, xgboost, SHAP | GPA prognozi, risk guruh aniqlash |
| **Infra** | Docker, Nginx, Sentry, Prometheus | Production deploy |

## Star Schema (TZ 6.2)

**Fakt jadval**: `fact_student_grades` (jn/on/yan, davomat, GPA points, kreditlar)

**7 dimension**:
1. `dim_student` — talaba
2. `dim_subject` — fan
3. `dim_teacher` — o'qituvchi
4. `dim_time` — sana/semestr
5. `dim_faculty` — fakultet
6. `dim_kafedra` — kafedra
7. `dim_group` — guruh

To'liq DDL: [`docs/schema_olap.sql`](./docs/schema_olap.sql)

## Ishga tushirish

### Talab qilinadigan dasturlar
- Docker Desktop 20+
- Docker Compose 2+
- 8 GB RAM (minimum)

### Tezkor start

```bash
# 1. Repository klonlash
git clone https://github.com/Muhammadqodir-Khakimov/unianalytics-pro.git
cd unianalytics-pro

# 2. Environment fayllarni tayyorlash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
cp apps/bot/.env.example apps/bot/.env       # Telegram bot tokeni

# 3. Servislarni ishga tushirish
make up                                      # yoki: docker-compose up -d

# 4. Migratsiyalar (multi-target)
make migrate                                 # OLTP + OLAP head'gacha

# 5. Test ma'lumotlari va ETL
make seed                                    # 5000+ talaba, 50000+ baho
make etl                                     # OLTP → OLAP ko'chirish
```

### Manzillar

| Servis | URL |
|--------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| Nginx (production) | http://localhost |
| Flower (Celery) | http://localhost:5555 |
| PostgreSQL OLTP | localhost:5432 |
| PostgreSQL OLAP | localhost:5433 |
| Redis | localhost:6379 |

## Test foydalanuvchilar

Default dev parollari (production'da `ADMIN_PASSWORD`, `DEKAN_PASSWORD`, `TEACHER_PASSWORD`, `STUDENT_PASSWORD` env-variablelari orqali beriladi).

| Rol | Login | Default parol |
|-----|-------|---------------|
| Admin | `admin` | `admin123` |
| Dekan | `dekan` | `dekan123` |
| O'qituvchi | `teacher` | `teacher123` |
| Talaba | `student` | `student123` |

## Loyiha strukturasi

```
unianalytics-pro/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/v1/           # REST endpointlar (50+ marshrut)
│   │   ├── models/oltp/      # Tranzaksion modellar (User, ParentLink, ...)
│   │   ├── models/olap/      # Star schema (1 fakt + 7 dim)
│   │   ├── olap/             # OLAP yadrosi (cube, query_builder, operations)
│   │   ├── ml/               # GPA forecast, dropout, anomaly, clustering, AI tutor
│   │   ├── services/         # Email, Telegram, notification, payment
│   │   └── tasks/            # Celery vazifalar
│   ├── alembic/              # Multi-target migratsiyalar (oltp/olap)
│   ├── scripts/              # seed_data, run_etl, migrate_parent_links_json_to_db
│   └── tests/                # pytest
├── frontend/                 # React 18 + TypeScript + Ant Design
│   └── src/pages/            # 30+ sahifa (admin, OLAP, ML, reports, ...)
├── apps/
│   ├── mobile/               # Flutter 3.16+ (iOS + Android)
│   │   └── lib/              # clean architecture: core/data/domain/presentation
│   ├── mobile-rn-archive/    # eski React Native kod (arxiv)
│   └── bot/                  # Telegram bot (aiogram 3)
│       └── bot/handlers/     # tz_commands.py — TZ 4.2.4 13 buyruq
├── docs/
│   ├── openapi.yaml          # to'liq REST API spetsifikatsiyasi
│   ├── schema_olap.sql       # PostgreSQL DWH DDL
│   ├── ARCHITECTURE.md       # tizim arxitekturasi
│   ├── DEPLOYMENT.md         # joriy etish
│   ├── SECURITY.md           # xavfsizlik
│   └── ...
├── infrastructure/
├── nginx/
├── docker-compose.yml        # backend + frontend + bot + redis + postgres
└── Makefile
```

## Tezkor buyruqlar (Makefile)

```bash
make up               # Servislar ishga tushirish (dev)
make down             # To'xtatish
make build            # Image'larni qayta qurish
make seed             # Test ma'lumotlar (5000+ talaba)
make etl              # OLTP → OLAP ko'chirish
make migrate          # OLTP + OLAP migratsiyalar (multi-target)
make migrate-oltp     # faqat OLTP head
make migrate-olap     # faqat OLAP head
make migrate-status   # joriy alembic revisiyalari
make test             # Backend testlar
make logs             # Loglarni kuzatish
make prod             # Production deploy
make clean            # Tozalash (volumes ham)
```

## Multi-target alembic

Loyiha **ikkita alohida ma'lumotlar bazasi** (OLTP va OLAP) bilan ishlaydi, lekin **bitta `versions/` papkadan** boshqariladi. Target `-x target=...` orqali tanlanadi:

```bash
alembic -x target=oltp current
alembic -x target=oltp upgrade oltp@head    # parent_links, user_preferences

alembic -x target=olap current
alembic -x target=olap upgrade olap@head    # dim_kafedra, dim_group, MV
```

Branch label'lar (`oltp`, `olap`) ikki chain'ni ajratadi — multi-head muammosi yo'q.

## Telegram bot (TZ 4.2.4)

**13 ta TZ-talab buyrug'i**:

| Buyruq | Vazifa |
|---|---|
| `/start` | Botni ishga tushirish |
| `/login` | Kirish |
| `/menu` | Asosiy menyu |
| `/reyting` | GPA va guruhdagi o'rin |
| `/fanlar` | Fanlar bo'yicha baholar |
| `/davomat` | Darslarga qatnashish foizi |
| `/jadval` | Dars jadvali |
| `/bogla <HEMIS_ID>` | Ota-ona ↔ farzand bog'lash |
| `/dayjest yoq\|ochir` | Haftalik dayjest |
| `/yordam` | Qo'llanma |
| `/aloqa` | Kurator/dekan kontaktlari |
| `/sozlamalar` | Til + bildirishnoma sozlamalari |
| `/chiqish` | Sessiyani yopish |

Buyruqlarning to'liq ko'rinishi: [`apps/bot/bot/handlers/tz_commands.py`](./apps/bot/bot/handlers/tz_commands.py)

## REST API

| Modul | URL prefiks | Tavsif |
|---|---|---|
| Auth | `/api/v1/auth/*` | JWT login, 2FA, refresh |
| OLAP | `/api/v1/olap/*` | Kub so'rovlari, drill-through, KPI |
| Mening hisobim | `/api/v1/my/*` | Dashboard, contacts, oqim |
| Bot | `/api/v1/bot/*` | link-parent (+approve/reject), parent-links |
| Sozlamalar | `/api/v1/users/me/preferences` | Dayjest, til, push |
| Hisobot | `/api/v1/reports/*` | PDF/Excel/CSV |
| ML | `/api/v1/ml/*` | Prognoz, risk guruh, clustering |
| HEMIS | `/api/v1/hemis/*` | Integratsiya |

To'liq OpenAPI 3.0 spec: [`docs/openapi.yaml`](./docs/openapi.yaml) yoki interaktiv Swagger: http://localhost:8000/docs

## CI/CD (GitHub Actions)

| Job | Tavsif |
|---|---|
| `backend-lint-test` | pytest + coverage + ruff + mypy |
| `frontend-lint-build` | npm lint + tsc + vite build |
| `bot-smoke-test` | TZ 4.2.4 13 buyruq mavjudligini tasdiqlash |
| `mobile-flutter` | flutter analyze + flutter test --coverage |
| `e2e-playwright` | chromium e2e |
| `docker-build` | backend + frontend + bot image'lari |

## Testlash

```bash
# Backend
docker-compose exec backend pytest -v
docker-compose exec backend pytest --cov=app --cov-report=html

# Frontend
cd frontend && npm test
cd frontend && npm run test:e2e        # Playwright

# Mobile
cd apps/mobile && flutter test --coverage

# Bot
cd apps/bot && pytest
```

## Hujjatlar

- [API spetsifikatsiyasi (OpenAPI)](./docs/openapi.yaml)
- [OLAP DWH DDL (PostgreSQL)](./docs/schema_olap.sql)
- [Arxitektura](./docs/ARCHITECTURE.md)
- [API hujjati](./docs/API.md)
- [OLAP modeli](./docs/OLAP_MODEL.md)
- [Deploy yo'riqnomasi](./docs/DEPLOYMENT.md)
- [Xavfsizlik](./docs/SECURITY.md)
- [Foydalanish qulayligi (A11Y)](./docs/A11Y.md)
- [Demo ssenariy](./docs/DEMO_SCRIPT.md)

## Litsenziya

Akademik maqsadlarda ishlab chiqilgan.
