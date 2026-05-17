# API Hujjati

Bu fayl barcha REST API endpointlarini hujjatlaydi. Real vaqtli Swagger UI: http://localhost:8000/docs

## Bazaviy URL

```
http://localhost:8000/api/v1
```

## Autentifikatsiya

JWT Bearer token. Login orqali olinadi va keyingi so'rovlarda yuboriladi:

```http
Authorization: Bearer <access_token>
```

## Endpointlar

### Auth
| Method | URL | Tavsif |
|--------|-----|--------|
| POST | `/auth/register` | Yangi user ro'yxati |
| POST | `/auth/login` | Login |
| POST | `/auth/refresh` | Token yangilash |
| GET | `/auth/me` | Joriy user |

### CRUD
| Method | URL | Tavsif |
|--------|-----|--------|
| GET/POST/PUT/DELETE | `/students` | Talabalar |
| GET/POST/PUT/DELETE | `/teachers` | O'qituvchilar |
| GET/POST/PUT/DELETE | `/subjects` | Fanlar |
| GET/POST/PUT/DELETE | `/grades` | Baholar |
| GET/POST/PUT/DELETE | `/faculties` | Fakultetlar |

### OLAP
| Method | URL | Tavsif |
|--------|-----|--------|
| POST | `/olap/query` | Dinamik OLAP so'rov |
| POST | `/olap/cube/aggregate` | Agregatsiya |
| POST | `/olap/drill-down` | Drill-down |
| POST | `/olap/roll-up` | Roll-up |
| POST | `/olap/slice` | Slice |
| POST | `/olap/dice` | Dice |
| POST | `/olap/pivot` | Pivot |
| GET | `/olap/dimensions` | O'lchovlar |
| GET | `/olap/measures` | O'lchamlar |

### Dashboard
| Method | URL | Tavsif |
|--------|-----|--------|
| GET | `/dashboard/summary` | Umumiy ko'rsatkichlar |
| GET | `/dashboard/gpa-trend` | GPA dinamikasi |
| GET | `/dashboard/faculty-comparison` | Fakultet solishtirma |
| GET | `/dashboard/top-students` | TOP-10 talaba |
| GET | `/dashboard/subject-performance` | Fanlar bo'yicha |

### Reports
| Method | URL | Tavsif |
|--------|-----|--------|
| POST | `/reports/generate/pdf` | PDF hisobot |
| POST | `/reports/generate/excel` | Excel hisobot |
| GET | `/reports/list` | Tayyor hisobotlar |

### ETL
| Method | URL | Tavsif |
|--------|-----|--------|
| POST | `/etl/run` | ETL ishga tushirish |
| GET | `/etl/status` | ETL holati |
