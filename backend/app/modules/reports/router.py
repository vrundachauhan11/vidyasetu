"""Regulatory Reports & Intelligence Module."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Institution, StudentEnrolment, IntegritySignal

router = APIRouter(prefix="/reports", tags=["Reports & Compliance Intelligence"])


@router.get("/summary")
async def get_regulatory_report_summary(db: AsyncSession = Depends(get_db)):
    """Generate consolidated regulatory intelligence summary for AICTE oversight."""
    inst_count = (await db.execute(select(func.count(Institution.id)))).scalar() or 0
    student_count = (await db.execute(select(func.count(StudentEnrolment.id)))).scalar() or 0
    verified_count = (await db.execute(select(func.count(StudentEnrolment.id)).where(StudentEnrolment.apaar_status == "VERIFIED"))).scalar() or 0
    pending_sig = (await db.execute(select(func.count(IntegritySignal.id)).where(IntegritySignal.review_status == "PENDING"))).scalar() or 0
    resolved_sig = (await db.execute(select(func.count(IntegritySignal.id)).where(IntegritySignal.review_status.like("RESOLVED%")))).scalar() or 0

    return {
        "success": True,
        "demo_mode": True,
        "report_id": "REP-AICTE-2026-Q1-INTEGRITY",
        "title": "National Technical Education Enrolment Integrity Scrutiny Report",
        "academic_year": "2025-26",
        "generated_for": "AICTE Approval & Regulatory Council",
        "kpis": {
            "institutions_audited": inst_count,
            "total_students_enrolled": student_count,
            "apaar_compliance_rate": f"{(verified_count / student_count * 100):.1f}%" if student_count else "0%",
            "active_review_signals": pending_sig,
            "resolved_triage_actions": resolved_sig,
        },
        "regulatory_findings": [
            {
                "category": "Intake Capacity",
                "finding": "1 seat overrun detected in B.Tech CSE (Apex Institute). Triaged under supernumerary category scrutiny.",
                "action": "Institutional clarification requested under Clause 4.1.",
            },
            {
                "category": "Identity Harmonisation",
                "finding": "Simulated APAAR matching achieved 80% direct confirmation; 20% undergoing phonetic normalization triage.",
                "action": "No student debarred; non-punitive review underway.",
            },
        ],
    }
