"""Overview Dashboard Router providing consolidated metrics and 7-stage workflow telemetry."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import (
    Institution,
    StudentEnrolment,
    IntegritySignal,
    IntakeBatch,
    AuditLog,
)

router = APIRouter(prefix="/dashboard", tags=["Overview Dashboard"])


@router.get("/overview")
async def get_dashboard_overview(db: AsyncSession = Depends(get_db)):
    """Fetch high-level telemetry and status across all institutions for the overview shell."""
    # Count institutions
    inst_res = await db.execute(select(func.count(Institution.id)))
    total_institutions = inst_res.scalar() or 0

    # Count students
    student_res = await db.execute(select(func.count(StudentEnrolment.id)))
    total_students = student_res.scalar() or 0

    # Count APAAR status
    verified_res = await db.execute(
        select(func.count(StudentEnrolment.id)).where(StudentEnrolment.apaar_status == "VERIFIED")
    )
    total_verified = verified_res.scalar() or 0

    pending_apaar_res = await db.execute(
        select(func.count(StudentEnrolment.id)).where(StudentEnrolment.apaar_status == "PENDING_VERIFICATION")
    )
    total_pending_apaar = pending_apaar_res.scalar() or 0

    mismatch_apaar_res = await db.execute(
        select(func.count(StudentEnrolment.id)).where(StudentEnrolment.apaar_status == "MISMATCH")
    )
    total_mismatch_apaar = mismatch_apaar_res.scalar() or 0

    apaar_verified_pct = round((total_verified / total_students * 100), 1) if total_students > 0 else 0.0

    # Count Signals
    signals_res = await db.execute(
        select(func.count(IntegritySignal.id)).where(IntegritySignal.review_status == "PENDING")
    )
    active_signals = signals_res.scalar() or 0

    # Count Audit Logs
    audit_res = await db.execute(select(func.count(AuditLog.id)))
    total_audit_logs = audit_res.scalar() or 0

    # Recent Batches
    batches_q = await db.execute(
        select(IntakeBatch).order_by(IntakeBatch.uploaded_at.desc()).limit(5)
    )
    batches = batches_q.scalars().all()
    batches_data = [
        {
            "id": b.id,
            "reference": b.batch_reference,
            "filename": b.filename,
            "academic_year": b.academic_year,
            "total_records": b.total_records,
            "valid_records": b.valid_records,
            "flagged_records": b.flagged_records,
            "status": b.status,
            "uploaded_at": b.uploaded_at.isoformat() if b.uploaded_at else "",
        }
        for b in batches
    ]

    # Recent Integrity Signals
    signals_q = await db.execute(
        select(IntegritySignal, StudentEnrolment.student_name, StudentEnrolment.enrolment_number)
        .join(StudentEnrolment, IntegritySignal.student_id == StudentEnrolment.id)
        .order_by(IntegritySignal.created_at.desc())
        .limit(5)
    )
    signals_rows = signals_q.all()
    signals_data = [
        {
            "id": sig.id,
            "rule_code": sig.rule_code,
            "severity": sig.severity,
            "finding_summary": sig.finding_summary,
            "explanation": sig.explanation,
            "review_status": sig.review_status,
            "student_name": name,
            "enrolment_number": enr,
            "created_at": sig.created_at.isoformat() if sig.created_at else "",
        }
        for sig, name, enr in signals_rows
    ]

    # 7-Stage Workflow Telemetry
    workflow_stages = [
        {
            "stage_number": 1,
            "name": "Data Intake & Ingestion",
            "description": "Upload institutional student roster in synthetic CSV format",
            "status": "OPERATIONAL",
            "active_count": len(batches_data),
            "badge": "Automated",
        },
        {
            "stage_number": 2,
            "name": "Schema & Type Validation",
            "description": "Field formatting, required columns, and date/category consistency checks",
            "status": "PASSING",
            "active_count": total_students,
            "badge": "Automated",
        },
        {
            "stage_number": 3,
            "name": "Simulated APAAR Validation",
            "description": "Deterministic lookup against simulated DigiLocker/APAAR registry adapter",
            "status": "SIMULATED_MOCK",
            "active_count": total_verified,
            "badge": "Simulated Adapter",
        },
        {
            "stage_number": 4,
            "name": "Intake Integrity Rules",
            "description": "Sanctioned intake capacity, duplicate enrolments, and quota verification",
            "status": "MONITORING",
            "active_count": active_signals,
            "badge": "Deterministic Engine",
        },
        {
            "stage_number": 5,
            "name": "Explainable Findings",
            "description": "Transparent rule evidence without opaque black-box scoring",
            "status": "READY",
            "active_count": active_signals,
            "badge": "Rule Transparency",
        },
        {
            "stage_number": 6,
            "name": "Evidence & Human Review",
            "description": "Institutional justification desk and regulatory triage queue",
            "status": "ACTION_REQUIRED" if active_signals > 0 else "CLEARED",
            "active_count": active_signals,
            "badge": "Human-in-the-Loop",
        },
        {
            "stage_number": 7,
            "name": "Repository & Cryptographic Audit",
            "description": "Versioned enrolment ledger with tamper-evident SHA-256 audit chaining",
            "status": "ACTIVE",
            "active_count": total_audit_logs,
            "badge": "Tamper-Evident",
        },
    ]

    return {
        "success": True,
        "demo_mode": True,
        "metrics": {
            "total_institutions": total_institutions,
            "total_students": total_students,
            "apaar_verified_pct": apaar_verified_pct,
            "total_verified": total_verified,
            "total_pending_apaar": total_pending_apaar,
            "total_mismatch_apaar": total_mismatch_apaar,
            "active_signals": active_signals,
            "total_audit_logs": total_audit_logs,
        },
        "workflow_stages": workflow_stages,
        "recent_batches": batches_data,
        "recent_signals": signals_data,
    }
