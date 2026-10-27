"""VidyaSetu - Main Application Entrypoint.
Product Positioning: An explainable, privacy-aware enrolment integrity and regulatory intelligence platform for AICTE-approved institutions.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import os
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.logging_config import setup_logging, logger
from app.database import AsyncSessionLocal, check_db_connection, engine, Base, get_db
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
    """Application lifecycle hooks: initialize schema and seed synthetic demo data on launch."""
    logger.info("Initializing VidyaSetu Regulatory Intelligence Platform...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema verified / created successfully.")
    except Exception as exc:
        logger.error(f"Error during schema creation: {exc}", exc_info=True)

    try:
        async with AsyncSessionLocal() as session:
            seed_stats = await seed_demo_data_if_empty(session)
            logger.info(f"Canonical demo data initialization result: {seed_stats}")
            dedup_count = await deduplicate_existing_signals(session)
            if dedup_count > 0:
                logger.info(f"Signal deduplication completed: removed {dedup_count} redundant signals.")
    except Exception as exc:
        logger.error(f"Error during demo data initialization: {exc}", exc_info=True)

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


@app.post(f"{settings.API_V1_PREFIX}/system/seed-demo", tags=["System Management"])
async def trigger_demo_seed(db: AsyncSession = Depends(get_db)):
    """Safe, idempotent endpoint to ensure canonical demo records exist in database."""
    try:
        stats = await seed_demo_data_if_empty(db)
        dedup_count = await deduplicate_existing_signals(db)
        return {
            "success": True,
            "message": "Canonical demo seed verified and synchronized successfully.",
            "stats": stats,
            "deduplicated_signals": dedup_count,
        }
    except Exception as exc:
        logger.error(f"Error during trigger_demo_seed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seed execution failed: {type(exc).__name__}: {str(exc)}",
        )


@app.get(f"{settings.API_V1_PREFIX}/system/seed-status", tags=["System Management"])
async def get_seed_status(db: AsyncSession = Depends(get_db)):
    """Check current database row counts for canonical demonstration data."""
    from sqlalchemy import select, func
    from app.models import Institution, ProgrammeApproval, StudentEnrolment, IntakeBatch, IntegritySignal, AuditLog

    inst_c = (await db.execute(select(func.count(Institution.id)))).scalar() or 0
    prog_c = (await db.execute(select(func.count(ProgrammeApproval.id)))).scalar() or 0
    st_c = (await db.execute(select(func.count(StudentEnrolment.id)))).scalar() or 0
    batch_c = (await db.execute(select(func.count(IntakeBatch.id)))).scalar() or 0
    sig_c = (await db.execute(select(func.count(IntegritySignal.id)))).scalar() or 0
    aud_c = (await db.execute(select(func.count(AuditLog.id)))).scalar() or 0

    return {
        "success": True,
        "counts": {
            "institutions": inst_c,
            "programmes": prog_c,
            "students": st_c,
            "batches": batch_c,
            "signals": sig_c,
            "audit_logs": aud_c,
        },
        "is_seeded": (st_c >= 13 and inst_c >= 3 and prog_c >= 4),
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

# Mount frontend production build if available (supports single-host deployment)
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if not os.path.exists(frontend_dist):
    frontend_dist = os.path.abspath("frontend/dist")

if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(full_path: str):
        # Do not intercept API requests
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        # Security: block access to sensitive extensions
        blocked = (".db", ".sqlite", ".sqlite3", ".env", ".bak", ".py", ".log", ".sh")
        if any(full_path.lower().endswith(ext) for ext in blocked):
            raise HTTPException(status_code=404, detail="Not Found")

        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

