# Student Rating OLAP System

**Talabalarning reyting natijalarini tahlil qilish uchun OLAP modelini ishlab chiqish**

Bitiruv malakaviy ishi (BMI) doirasida ishlab chiqilgan universitet talabalarining reyting natijalarini ko'p o'lchovli tahlil qilish tizimi.

**Ilmiy rahbar:** Onarkulov Maksadjon Karimberdiyevich

---

## Loyiha haqida

Tizim **OLAP (Online Analytical Processing)** modeliga asoslangan bo'lib, talabalar reyting ma'lumotlarini ko'p o'lchovli kub (cube) ko'rinishida tahlil qilish imkonini beradi. Asosiy operatsiyalar:

- **Drill-down / Roll-up** — Universitet ↔ Fakultet ↔ Guruh ↔ Talaba
- **Slice / Dice** — bir yoki bir nechta o'lchov bo'yicha filtrlash
- **Pivot** — o'lchovlarni almashtirish
- **CUBE / ROLLUP / GROUPING SETS** — SQL darajasida agregatsiya

## Texnik stack

### Backend
- Python 3.11 + FastAPI
- PostgreSQL 16 (OLTP) + PostgreSQL (OLAP Data Warehouse)
- SQLAlchemy 2.0 + Alembic
- Celery + Redis (ETL)
- JWT authentication

### Frontend
- React 18 + TypeScript + Vite
- Ant Design + TailwindCSS
- Apache ECharts + Recharts
- TanStack Query + Zustand
- i18next (uz/ru/en)

### Infrastructure
- Docker + Docker Compose
- Nginx (reverse proxy)

## Ishga tushirish

### Talab qilinadigan dasturlar
- Docker Desktop 20+
- Docker Compose 2+
- 8 GB RAM (minimum)

### Tezkor start

```bash
# 1. Repository klonlash
git clone <repo-url>
cd student-rating-olap

# 2. Environment fayllarni tayyorlash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 3. Docker bilan ishga tushirish
docker-compose up -d

# 4. Database migratsiyalar
docker-compose exec backend alembic upgrade head

# 5. Test ma'lumotlarini yuklash (50,000+ baho)
docker-compose exec backend python scripts/seed_data.py

# 6. ETL ishga tushirish (OLTP -> OLAP)
docker-compose exec backend python scripts/run_etl.py
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

| Rol | Login | Parol |
|-----|-------|-------|
| Admin | `admin` | `admin123` |
| Dekan | `dekan` | `dekan123` |
| O'qituvchi | `teacher` | `teacher123` |
| Talaba | `student` | `student123` |

## Loyiha strukturasi

```
student-rating-olap/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── nginx/            # Nginx config
├── docs/             # Hujjatlar (API, OLAP model, deploy)
└── docker-compose.yml
```

## Hujjatlar

- [API hujjati](./docs/API.md)
- [OLAP modeli (Star Schema)](./docs/OLAP_MODEL.md)
- [Deploy yo'riqnomasi](./docs/DEPLOYMENT.md)

## Tezkor buyruqlar (Makefile)

```bash
make up        # Servislar ishga tushirish
make seed      # Test ma'lumotlar (5000 talaba, 50000+ baho)
make etl       # OLTP -> OLAP ko'chirish
make test      # Backend testlar
make logs      # Loglarni kuzatish
make prod      # Production deploy
make clean     # Tozalash
```

## Loyiha tarkibi

### Backend modullari
- `app/main.py` — FastAPI entry point
- `app/config.py` — Pydantic settings
- `app/database.py` — OLTP + OLAP engines
- `app/models/oltp/` — Transactional modellar
- `app/models/olap/` — Star schema (fact + 6 dim)
- `app/olap/` — **OLAP Core** (cube, query_builder, operations)
- `app/api/v1/` — REST endpointlar
- `app/services/` — Biznes logika
- `app/tasks/` — Celery vazifalar

### Frontend tarkibi
- `src/pages/` — sahifalar (dashboard, OLAP, CRUD, reports)
- `src/components/` — qayta ishlatiluvchi komponentlar
- `src/services/` — API klientlar
- `src/store/` — Zustand store
- `src/locales/` — i18n (uz/ru/en)

## OLAP Operatsiyalari

| Operatsiya | Endpoint | Tavsif |
|-----------|----------|--------|
| Query | `POST /olap/query` | Universal |
| Slice | `POST /olap/slice` | 1 o'lchov filter |
| Dice | `POST /olap/dice` | N filter |
| Drill-down | `POST /olap/drill-down` | Yuqori → past |
| Roll-up | `POST /olap/roll-up` | Past → yuqori |
| Pivot | `POST /olap/pivot` | Matritsa |
| Cube | `POST /olap/cube/aggregate` | CUBE/ROLLUP |

## Testlash

```bash
# Backend
docker-compose exec backend pytest -v

# Coverage
docker-compose exec backend pytest --cov=app --cov-report=html
```

## Litsenziya

Akademik maqsadlarda ishlab chiqilgan.
