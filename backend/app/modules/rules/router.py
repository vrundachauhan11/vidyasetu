"""Rule Registry & Intake Integrity Monitoring Module."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import IntegritySignal, StudentEnrolment

router = APIRouter(prefix="/rules", tags=["Rule Registry & Integrity Monitoring"])

# Standard AICTE Enrolment Integrity Deterministic Rules
RULE_REGISTRY = [
    {
        "code": "R01_SANCTIONED_INTAKE_EXCEEDED",
        "title": "Sanctioned Intake Capacity Limit",
        "category": "Capacity & Regulatory Approval",
        "severity": "HIGH",
        "regulatory_reference": "AICTE Approval Process Handbook (APH) 2024-27, Clause 4.1",
        "description": "Verifies that total enrolled students in any approved programme do not exceed the sanctioned intake approved in the Extension of Approval (EOA).",
        "status": "ACTIVE",
    },
    {
        "code": "R02_APAAR_NAME_DISCREPANCY",
        "title": "APAAR Identity & Name Discrepancy",
        "category": "Identity Verification",
        "severity": "MEDIUM",
        "regulatory_reference": "Ministry of Education National Credit Framework (NCrF) & APAAR Mandate",
        "description": "Compares spelling and phonetic distance between institute admission record and simulated APAAR registry. Flags for human review if variation is detected.",
        "status": "ACTIVE",
    },
    {
        "code": "R03_DUPLICATE_CONCURRENT_ENROLMENT",
        "title": "Concurrent Full-Time Enrolment Check",
        "category": "Enrolment Exclusivity",
        "severity": "HIGH",
        "regulatory_reference": "UGC/AICTE Guidelines on Dual Academic Programmes",
        "description": "Ensures an APAAR identifier is not actively enrolled in two simultaneous full-time technical programmes without dual-degree approval.",
        "status": "ACTIVE",
    },
    {
        "code": "R04_PREREQUISITE_DEFICIT",
        "title": "Minimum Eligibility & Prerequisite Check",
        "category": "Academic Prerequisite",
        "severity": "MEDIUM",
        "regulatory_reference": "AICTE APH Clause 5.2 - Minimum Entry Qualifications",
        "description": "Flags records where entry qualification credentials require secondary verification.",
        "status": "ACTIVE",
    },
    {
        "code": "R05_STATE_QUOTA_ANOMALY",
        "title": "Approved Quota Allocation Adherence",
        "category": "Quota & Equity Compliance",
        "severity": "LOW",
        "regulatory_reference": "State Admission Regulatory Committee (SARC) Allotment Guidelines",
        "description": "Monitors ratio of State Merit vs Institutional/Management quota enrolments against sanctioned limits.",
        "status": "ACTIVE",
    },
    {
        "code": "R06_SUPERNUMERARY_CAP_EXCEEDED",
        "title": "Supernumerary Seat Ceiling (TFWS/EWS/PMSSS)",
        "category": "Quota & Equity Compliance",
        "severity": "MEDIUM",
        "regulatory_reference": "AICTE Tuition Fee Waiver Scheme (TFWS) Guidelines",
        "description": "Validates that supernumerary allocations strictly conform to statutory ceilings (e.g., 5% TFWS).",
        "status": "ACTIVE",
    },
]


@router.get("")
async def list_registered_rules():
    """List all deterministic intake integrity rules in the active registry."""
    return {
        "success": True,
        "demo_mode": True,
        "count": len(RULE_REGISTRY),
        "data": RULE_REGISTRY,
    }


@router.get("/signals")
async def list_active_signals(db: AsyncSession = Depends(get_db)):
    """Fetch all active integrity signals with explainable findings."""
    stmt = (
        select(IntegritySignal, StudentEnrolment.student_name, StudentEnrolment.enrolment_number, StudentEnrolment.apaar_id)
        .join(StudentEnrolment, IntegritySignal.student_id == StudentEnrolment.id)
        .order_by(IntegritySignal.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return {
        "success": True,
        "demo_mode": True,
        "count": len(rows),
        "data": [
            {
                "id": sig.id,
                "student_id": sig.student_id,
                "student_name": s_name,
                "enrolment_number": s_enr,
                "apaar_id": s_apaar or "N/A",
                "rule_code": sig.rule_code,
                "severity": sig.severity,
                "finding_summary": sig.finding_summary,
                "explanation": sig.explanation,
                "review_status": sig.review_status,
                "reviewer_decision": sig.reviewer_decision,
                "reviewer_notes": sig.reviewer_notes,
                "created_at": sig.created_at.isoformat() if sig.created_at else "",
            }
            for sig, s_name, s_enr, s_apaar in rows
        ],
    }
