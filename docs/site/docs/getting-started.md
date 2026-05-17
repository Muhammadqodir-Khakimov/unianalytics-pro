---
sidebar_position: 2
---

# Tezkor boshlash

## Talab

- Python 3.11+ (lokal dev)
- Node.js 18+
- PostgreSQL 14+ yoki SQLite (dev)
- Docker (ixtiyoriy)

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m app.scripts.seed_data
uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Brauzerda oching: http://localhost:5173

## Default akkauntlar

| Rol | Username | Parol |
|-----|----------|-------|
| Admin | `admin` | `admin123` |
| Dekan | `dekan_iqtisod` | `dekan123` |
| Teacher | `teacher_math` | `teacher123` |
| Student | `student001` | `student123` |
