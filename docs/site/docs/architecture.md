---
sidebar_position: 3
---

# Arxitektura

## Yuqori sath

```
┌──────────────────────────────────────────┐
│  Frontend (React 18 + TS + Ant Design 5) │
│  PWA + Mobile (React Native + Expo)       │
└────────────────┬─────────────────────────┘
                 │ HTTPS / WebSocket
┌────────────────▼─────────────────────────┐
│  FastAPI Backend (Python 3.11+)          │
│  JWT + 2FA + OAuth                       │
└──┬──────┬───────┬───────┬────────┬───────┘
   │      │       │       │        │
┌──▼──┐┌──▼──┐┌───▼───┐┌──▼──┐┌────▼────┐
│OLTP ││OLAP ││ Redis ││ ML  ││Celery   │
│PgSQL││PgSQL││ Cache ││XGB+ ││Beat+    │
│     ││Star ││       ││SHAP ││Workers  │
└─────┘└─────┘└───────┘└─────┘└─────────┘
```

## Ma'lumotlar oqimi

1. **OLTP** — kunlik amallar (login, baho qo'yish, ariza)
2. **ETL** (har soatda) — OLTP → OLAP star schema
3. **OLAP** — Cube/Pivot/Reports
4. **ML pipeline** (haftalik) — model retrain
5. **Cache (Redis/in-memory)** — agregat natijalar

## Star Schema (OLAP)

- **fact_grades** — markaziy fakt jadval
- **dim_time** — kun / oy / chorak / yil
- **dim_student** — talaba o'lchovi (SCD Type 2)
- **dim_subject** — fan o'lchovi
- **dim_faculty** — fakultet o'lchovi
- **dim_teacher** — o'qituvchi o'lchovi
