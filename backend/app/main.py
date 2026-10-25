"""VidyaSetu - Main Application Entrypoint.
Product Positioning: An explainable, privacy-aware enrolment integrity and regulatory intelligence platform for AICTE-approved institutions.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.logging_config import setup_logging, logger
from app.database import AsyncSessionLocal, check_db_connection
from app.core.errors import (
    VidyaSetuException,
    vidyasetu_exception_handler,
    global_exception_handler,
)
from app.seed.demo_data import seed_demo_data_if_empty
from app.modules.intake.deduplicate import deduplicate_existing_signals

# Module Routers
from app.modules.auth.router import router as auth_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.institutions.router import router as institutions_router
from app.modules.students.router import router as students_router
from app.modules.intake.router import router as intake_router
from app.modules.apaar.router import router as apaar_router
from app.modules.rules.router import router as rules_router
from app.modules.review.router import router as review_router
from app.modules.credentials.router import router as credentials_router
from app.modules.consent.router import router as consent_router
from app.modules.audit.router import router as audit_router
from app.modules.reports.router import router as reports_router

setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle hooks: seed synthetic demo data on launch."""
    logger.info("Initializing VidyaSetu Regulatory Intelligence Platform...")
    try:
        async with AsyncSessionLocal() as session:
            await seed_demo_data_if_empty(session)
            await deduplicate_existing_signals(session)
    except Exception as exc:
        logger.warning(f"Initial DB seed / deduplication check skipped or deferred: {exc}")
    yield
    logger.info("Shutting down VidyaSetu API gracefully.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Explainable, privacy-aware enrolment integrity and regulatory intelligence platform for AICTE-approved institutions.",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Exception Handlers
app.add_exception_handler(VidyaSetuException, vidyasetu_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configurable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{settings.API_V1_PREFIX}/health", tags=["System Health"])
async def get_health():
    """System health probe checking database connectivity and simulation services."""
    db_status = await check_db_connection()
    is_healthy = db_status["connected"]

    content = {
        "status": "healthy" if is_healthy else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_status,
        "simulation_mode": {
            "is_demo": True,
            "apaar_adapter": "SIMULATED_MOCK" if settings.ENABLE_MOCK_APAAR else "LIVE",
            "aicte_registry": "SIMULATED_MOCK" if settings.AICTE_COUNCIL_REGISTRY_MOCK else "LIVE",
            "disclaimer": "DEMO DATA ONLY - All student identities and external checks are simulated.",
        },
    }

    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=content)


@app.get(f"{settings.API_V1_PREFIX}/version", tags=["System Health"])
async def get_version():
    """System version, product positioning and build details."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "product_positioning": "An explainable, privacy-aware enrolment integrity and regulatory intelligence platform for AICTE-approved institutions.",
        "problem_statement": "SIH 2026 Problem Statement 26263",
        "demo_mode": True,
        "disclaimer": "DEMO DATA ONLY - External integrations are simulated.",
    }


# Include Routers with API Prefix
api_prefix = settings.API_V1_PREFIX
app.include_router(auth_router, prefix=api_prefix)
app.include_router(dashboard_router, prefix=api_prefix)
app.include_router(institutions_router, prefix=api_prefix)
app.include_router(students_router, prefix=api_prefix)
app.include_router(intake_router, prefix=api_prefix)
app.include_router(apaar_router, prefix=api_prefix)
app.include_router(rules_router, prefix=api_prefix)
app.include_router(review_router, prefix=api_prefix)
app.include_router(credentials_router, prefix=api_prefix)
app.include_router(consent_router, prefix=api_prefix)
app.include_router(audit_router, prefix=api_prefix)
app.include_router(reports_router, prefix=api_prefix)
