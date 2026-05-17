# 🏗️ UniAnalytics PRO — Architecture

## System Overview

```mermaid
graph TB
    subgraph "Foydalanuvchilar"
        U1[👨‍🎓 Talaba]
        U2[👨‍🏫 O'qituvchi]
        U3[👨‍💼 Dekan]
        U4[⚙️ Admin]
    end

    subgraph "Frontend"
        WEB[React + Vite<br/>Ant Design + TS]
        TG[Telegram Bot<br/>aiogram]
        MOB[React Native<br/>iOS/Android]
    end

    subgraph "API Gateway"
        NGINX[Nginx<br/>SSL, Rate Limit]
    end

    subgraph "Backend"
        API[FastAPI<br/>173+ endpoints]
        CELERY[Celery Worker<br/>ETL, ML training]
        BEAT[Celery Beat<br/>Scheduled tasks]
    end

    subgraph "Data Layer"
        OLTP[(PostgreSQL OLTP<br/>Transactional)]
        OLAP[(PostgreSQL OLAP<br/>Star Schema)]
        REDIS[(Redis<br/>Cache + Queue)]
        S3[(File Storage<br/>S3/MinIO)]
    end

    subgraph "ML / AI"
        XGB[XGBoost<br/>Drop-out]
        KMEANS[K-Means<br/>Segmentation]
        FCAST[Forecasting<br/>Polynomial]
        ISOF[Isolation Forest<br/>Anomaly]
        AI[AI Tutor<br/>Claude/OpenAI]
    end

    subgraph "Integrations"
        HEMIS[HEMIS API]
        MOODLE[Moodle LMS]
        ESKIZ[Eskiz SMS]
        CLICK[Click Payment]
        PAYME[Payme]
    end

    subgraph "Monitoring"
        SENTRY[Sentry<br/>Errors]
        PROM[Prometheus<br/>Metrics]
        AUDIT[Audit Log]
    end

    U1 --> WEB & TG & MOB
    U2 & U3 & U4 --> WEB
    WEB & TG & MOB --> NGINX
    NGINX --> API
    API --> OLTP & OLAP & REDIS & S3
    API --> XGB & KMEANS & FCAST & ISOF & AI
    API --> HEMIS & MOODLE & ESKIZ & CLICK & PAYME
    CELERY --> OLTP & OLAP
    BEAT --> CELERY
    API --> SENTRY & PROM & AUDIT
```

---

## Star Schema (OLAP)

```mermaid
erDiagram
    FACT_STUDENT_GRADES ||--o{ DIM_STUDENT : "student_key"
    FACT_STUDENT_GRADES ||--o{ DIM_SUBJECT : "subject_key"
    FACT_STUDENT_GRADES ||--o{ DIM_TEACHER : "teacher_key"
    FACT_STUDENT_GRADES ||--o{ DIM_TIME : "time_key"
    FACT_STUDENT_GRADES ||--o{ DIM_FACULTY : "faculty_key"
    FACT_STUDENT_GRADES ||--o{ DIM_ASSESSMENT_TYPE : "assessment_type_key"

    FACT_STUDENT_GRADES {
        bigint grade_id PK
        int student_key FK
        int subject_key FK
        int teacher_key FK
        int time_key FK
        int faculty_key FK
        int assessment_type_key FK
        decimal grade_value
        int credit_hours
        decimal attendance_percentage
        decimal gpa_points
        bool is_passed
    }

    DIM_STUDENT {
        int student_key PK
        string student_id
        string full_name
        char gender
        date birth_date
        int enrollment_year
        string group_name
        string education_form
        string status
    }

    DIM_SUBJECT {
        int subject_key PK
        string subject_code
        string subject_name
        string department
        int credit_hours
        string subject_type
        int semester
    }

    DIM_TEACHER {
        int teacher_key PK
        string teacher_id
        string full_name
        string academic_degree
        string position
        string department
    }

    DIM_TIME {
        int time_key PK
        date full_date
        int day
        int week
        int month
        int quarter
        string semester
        string academic_year
        int year
    }

    DIM_FACULTY {
        int faculty_key PK
        string faculty_name
        string specialty
        int course
        string group_name
    }

    DIM_ASSESSMENT_TYPE {
        int assessment_type_key PK
        string type_name
        decimal weight_percentage
    }
```

---

## OLAP Operations Flow

```mermaid
flowchart LR
    USER[👤 User Query] --> UI[Frontend UI]
    UI --> |HTTP POST| API[FastAPI]
    API --> QB[Query Builder]
    QB --> |Validate dims/measures| CUBE[Cube Definition]
    CUBE --> SQL[SQL Generator]
    SQL --> |CUBE/ROLLUP| DB[(OLAP DB)]
    DB --> |Result rows| CACHE[Redis Cache]
    CACHE --> JSON[JSON Response]
    JSON --> UI
    UI --> |ECharts/Pivot| CHART[Visualization]

    subgraph "OLAP Operations"
        SLICE[Slice]
        DICE[Dice]
        DRILL[Drill-down]
        ROLL[Roll-up]
        PIVOT[Pivot]
        CUBE_OP[CUBE/ROLLUP]
    end

    QB --> SLICE & DICE & DRILL & ROLL & PIVOT & CUBE_OP
```

---

## ML Pipeline

```mermaid
flowchart TB
    subgraph "Data Sources"
        OLTP[(OLTP DB)]
        OLAP[(OLAP DB)]
        HEMIS_API[HEMIS API]
    end

    subgraph "Feature Engineering"
        FE[Feature Extraction<br/>GPA, attendance,<br/>failed_count, etc.]
    end

    subgraph "ML Models"
        XGB[XGBoost Classifier<br/>Drop-out prediction]
        KMEANS[K-Means<br/>Student segmentation]
        POLY[Polynomial Regression<br/>GPA forecasting]
        ISOF[Isolation Forest<br/>Anomaly detection]
        AI[Claude/OpenAI<br/>AI Tutor]
    end

    subgraph "Outputs"
        RISK[Risk Score 0-1<br/>+ SHAP explanation]
        CLUSTER[Cluster Label<br/>5 categories]
        PRED[Next semester GPA<br/>+ CI 95%]
        ANOM[Anomaly Score]
        CHAT[Chat Response]
    end

    OLTP & OLAP --> FE
    HEMIS_API --> FE
    FE --> XGB --> RISK
    FE --> KMEANS --> CLUSTER
    FE --> POLY --> PRED
    FE --> ISOF --> ANOM
    OLAP --> AI --> CHAT

    RISK --> DASH[Dean Dashboard]
    CLUSTER --> DASH
    PRED --> SDASH[Student Dashboard]
    ANOM --> DASH
    CHAT --> SDASH
```

---

## Authentication & Authorization Flow

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant API
    participant DB
    participant Redis

    User->>Frontend: Login (username, password)
    Frontend->>API: POST /api/v1/auth/login
    API->>DB: Verify password (bcrypt)
    DB-->>API: User + role
    API->>API: Generate JWT access + refresh
    API-->>Frontend: tokens
    Frontend->>Frontend: Store in Zustand (localStorage)

    Note over User,Redis: Subsequent requests
    User->>Frontend: Click "Students"
    Frontend->>API: GET /students<br/>Authorization: Bearer {token}
    API->>API: Decode JWT, check role
    API->>API: Check permission (student.read)
    API->>Redis: Cache check
    Redis-->>API: Hit/Miss
    API->>DB: Query if miss
    DB-->>API: Students
    API-->>Frontend: JSON
    Frontend-->>User: Render table
```

---

## Multi-Tenant Architecture

```mermaid
graph TB
    DNS[DNS] --> |tdu.unianalytics.uz| LB[Load Balancer]
    DNS --> |samdu.unianalytics.uz| LB
    DNS --> |bukhdu.unianalytics.uz| LB

    LB --> |Host header| TENANT[Tenant Resolver]
    TENANT --> |TDU| ROUTE1[API instance]
    TENANT --> |SamDU| ROUTE2[API instance]
    TENANT --> |BukhDU| ROUTE3[API instance]

    ROUTE1 --> SCHEMA1[(tdu_schema)]
    ROUTE2 --> SCHEMA2[(samdu_schema)]
    ROUTE3 --> SCHEMA3[(bukhdu_schema)]

    SCHEMA1 & SCHEMA2 & SCHEMA3 --> SHARED[(Shared OLAP)]
```

---

## Deployment Architecture

```mermaid
graph LR
    subgraph "GitHub"
        REPO[unianalytics-pro]
        ACTIONS[GitHub Actions]
    end

    subgraph "Hosting"
        RAILWAY[Railway / Render]
        DOCKER[Docker Compose]
    end

    subgraph "External Services"
        DOMAIN[Domain<br/>unianalytics.uz]
        CLOUDFLARE[Cloudflare<br/>CDN + DDoS]
        SENTRY[Sentry]
        ANALYTICS[Plausible Analytics]
    end

    REPO --> |push main| ACTIONS
    ACTIONS --> |Test, Build| RAILWAY
    ACTIONS --> |Docker push| DOCKER
    DOMAIN --> CLOUDFLARE
    CLOUDFLARE --> RAILWAY
    RAILWAY --> SENTRY
    RAILWAY --> ANALYTICS
```

---

## Telegram Bot Integration

```mermaid
sequenceDiagram
    actor Student
    participant Bot
    participant Backend
    participant DB

    Student->>Bot: /start
    Bot->>Student: Welcome message

    Student->>Bot: /link ST202500001
    Bot->>Backend: Check student exists
    Backend->>DB: Query Student
    DB-->>Backend: Student data
    Backend-->>Bot: OK
    Bot->>Bot: Save chat_id → student_id
    Bot->>Student: ✅ Linked

    Note over Student,DB: Talaba so'rovlari
    Student->>Bot: /balls
    Bot->>Backend: Get recent grades
    Backend->>DB: Query last 10
    DB-->>Backend: Grades
    Backend-->>Bot: Formatted
    Bot->>Student: 📝 Last grades

    Note over Backend,Student: Avtomatik xabarlar
    DB-->>Backend: New grade event
    Backend->>Bot: Notify chat_id
    Bot->>Student: 🟢 New grade: 85
```
