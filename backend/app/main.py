"""FastAPI ilovasini boshlang'ich nuqtasi."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import (
    analytics as analytics_router,
    applications as applications_router,
    audit as audit_router,
    auth as auth_router,
    bmi as bmi_router,
    cache_admin as cache_router,
    certificate as certificate_router,
    dashboard as dashboard_router,
    health as health_router,
    detail as detail_router,
    etl as etl_router,
    faculties as faculties_router,
    grades as grades_router,
    hemis as hemis_router,
    imports as imports_router,
    ml_api as ml_router,
    billing as billing_router,
    integrations as integrations_router,
    multicube as multicube_router,
    my as my_router,
    onboarding as onboarding_router,
    notifications as notifications_router,
    olap as olap_router,
    reports as reports_router,
    schedule as schedule_router,
    scholarship as scholarship_router,
    search as search_router,
    students as students_router,
    subjects as subjects_router,
    teachers as teachers_router,
    telegram as telegram_router,
    bot_endpoints as bot_endpoints_router,
    permissions as permissions_router,
    tenants as tenants_router,
    transcript as transcript_router,
    uploads as uploads_router,
    users as users_router,
    webhooks as webhooks_router,
)
from app.config import settings
from app.core.monitoring import setup_prometheus, setup_sentry
from app.core.rate_limit import setup_rate_limiting


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    description="Talabalarning reyting natijalarini OLAP modeli orqali tahlil qilish — Production Edition",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monitoring va observability
setup_sentry(app)
setup_prometheus(app)
setup_rate_limiting(app)

API_V1_PREFIX = "/api/v1"

# Asosiy
app.include_router(auth_router.router, prefix=API_V1_PREFIX)
app.include_router(users_router.router, prefix=API_V1_PREFIX)
app.include_router(notifications_router.router, prefix=API_V1_PREFIX)

# CRUD
app.include_router(faculties_router.router, prefix=API_V1_PREFIX)
app.include_router(students_router.router, prefix=API_V1_PREFIX)
app.include_router(teachers_router.router, prefix=API_V1_PREFIX)
app.include_router(subjects_router.router, prefix=API_V1_PREFIX)
app.include_router(grades_router.router, prefix=API_V1_PREFIX)

# OLAP, Analytics va ML
app.include_router(olap_router.router, prefix=API_V1_PREFIX)
app.include_router(dashboard_router.router, prefix=API_V1_PREFIX)
app.include_router(analytics_router.router, prefix=API_V1_PREFIX)
app.include_router(ml_router.router, prefix=API_V1_PREFIX)
app.include_router(multicube_router.router, prefix=API_V1_PREFIX)
app.include_router(billing_router.router, prefix=API_V1_PREFIX)
app.include_router(integrations_router.router, prefix=API_V1_PREFIX)
app.include_router(onboarding_router.router, prefix=API_V1_PREFIX)
app.include_router(bmi_router.router, prefix=API_V1_PREFIX)
app.include_router(health_router.router, prefix=API_V1_PREFIX)

# Mening hisobim va detail
app.include_router(my_router.router, prefix=API_V1_PREFIX)
app.include_router(detail_router.router, prefix=API_V1_PREFIX)
app.include_router(search_router.router, prefix=API_V1_PREFIX)

# Akademik (jadval, davomat, ariza, ma'lumotnoma, transkript, stipendiya)
app.include_router(schedule_router.router, prefix=API_V1_PREFIX)
app.include_router(applications_router.router, prefix=API_V1_PREFIX)
app.include_router(scholarship_router.router, prefix=API_V1_PREFIX)
app.include_router(certificate_router.router, prefix=API_V1_PREFIX)
app.include_router(transcript_router.router, prefix=API_V1_PREFIX)

# Hisobotlar va import
app.include_router(reports_router.router, prefix=API_V1_PREFIX)
app.include_router(imports_router.router, prefix=API_V1_PREFIX)

# HEMIS-style features (announcements, payments, exams, thesis, library, dormitory, documents, messaging)
app.include_router(hemis_router.router, prefix=API_V1_PREFIX)
app.include_router(uploads_router.router, prefix=API_V1_PREFIX)

# Admin va Enterprise
app.include_router(etl_router.router, prefix=API_V1_PREFIX)
app.include_router(audit_router.router, prefix=API_V1_PREFIX)
app.include_router(cache_router.router, prefix=API_V1_PREFIX)
app.include_router(telegram_router.router, prefix=API_V1_PREFIX)
app.include_router(bot_endpoints_router.router, prefix=API_V1_PREFIX)
app.include_router(tenants_router.router, prefix=API_V1_PREFIX)
app.include_router(permissions_router.router, prefix=API_V1_PREFIX)
app.include_router(webhooks_router.router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["System"])
async def health_check() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "ok",
            "service": settings.app_name,
            "environment": settings.app_env,
            "version": "3.0.0",
        }
    )


@app.get("/", tags=["System"])
async def root() -> dict:
    return {
        "message": "Student Rating OLAP API",
        "docs": "/docs",
        "health": "/health",
        "version": "3.0.0",
    }
