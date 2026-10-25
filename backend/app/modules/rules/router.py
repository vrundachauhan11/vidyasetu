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
        "regulatory_reference": "AICTE Approval Process Handbook (APH) 2024-27, Chap. IV/V [DEMO CLAUSE CITATION - Principle Verified: Excess Admissions Prohibited under AICTE Act 1987 §10(k)]",
        "description": "Evaluates whether cumulative student enrolments exceed the statutory sanctioned intake approved in the institutional Extension of Approval (EOA). Intake ceiling is evaluated dynamically against institutional approval limits [DEMO CONFIGURATION].",
        "status": "ACTIVE",
        "implementation_status": "OPERATIONAL",
        "reference_status": "VERIFIED_STATUTORY",
    },
    {
        "code": "R02_APAAR_NAME_DISCREPANCY",
        "title": "APAAR Identity & Name Discrepancy",
        "category": "Identity Verification",
        "severity": "MEDIUM",
        "regulatory_reference": "Ministry of Education (MoE) / AICTE APAAR Mandate [Statutory Directive Verified; Phonetic Threshold 88% is DEMO CONFIGURATION]",
        "description": "Compares spelling and phonetic distance between admission roster and simulated APAAR registry. Flags for human review if variation is detected. Matching cutoff is a platform heuristic [DEMO CONFIGURATION].",
        "status": "ACTIVE",
        "implementation_status": "OPERATIONAL",
        "reference_status": "VERIFIED_STATUTORY",
    },
    {
        "code": "R02_APAAR_PENDING_ACKNOWLEDGEMENT",
        "title": "APAAR Verification Pending Acknowledgment",
        "category": "Identity Verification",
        "severity": "LOW",
        "regulatory_reference": "AICTE / NCrF Digital Verification Protocol [DEMO SPECIFICATION - Operational Handshake]",
        "description": "Simulated APAAR adapter handshake is pending operational acknowledgment. Non-punitive operational sync state; requires retry/sync verification rather than fraud investigation.",
        "status": "ACTIVE",
        "implementation_status": "OPERATIONAL",
        "reference_status": "DEMO_REFERENCE",
    },
    {
        "code": "R02_APAAR_UNAVAILABLE_IN_ROSTER",
        "title": "APAAR Identifier Missing from Admission Roster",
        "category": "Identity Verification",
        "severity": "LOW",
        "regulatory_reference": "National Education Policy (NEP 2020) APAAR Adoption Guidelines [DEMO SPECIFICATION]",
        "description": "Student record was submitted without an APAAR ID provided in the admission roster. Flags for institutional follow-up to obtain identity documentation. Missing status is an operational data gap, not fraud.",
        "status": "ACTIVE",
        "implementation_status": "OPERATIONAL",
        "reference_status": "DEMO_REFERENCE",
    },
    {
        "code": "R02_APAAR_MOCK_DISCREPANCY",
        "title": "APAAR Simulated Registry Discrepancy",
        "category": "Identity Verification",
        "severity": "MEDIUM",
        "regulatory_reference": "AICTE / APAAR Data Integrity Guidelines [DEMO SPECIFICATION - Legacy Adapter Alias]",
        "description": "Simulated APAAR registry returned a discrepancy flag requiring human reviewer triage. Retained for historical test event compatibility.",
        "status": "ACTIVE",
        "implementation_status": "OPERATIONAL",
        "reference_status": "DEMO_REFERENCE",
    },
    {
        "code": "R03_DUPLICATE_CONCURRENT_ENROLMENT",
        "title": "Concurrent Full-Time Enrolment Check",
        "category": "Enrolment Exclusivity",
        "severity": "HIGH",
        "regulatory_reference": "UGC Guidelines for Pursuing Two Academic Programmes Simultaneously (April 2022) [VERIFIED STATUTORY]",
        "description": "Ensures an APAAR identifier or enrolment identifier is not actively enrolled in two simultaneous full-time technical programmes without statutory dual-degree approval.",
        "status": "ACTIVE",
        "implementation_status": "OPERATIONAL",
        "reference_status": "VERIFIED_STATUTORY",
    },
    {
        "code": "R04_PREREQUISITE_DEFICIT",
        "title": "Minimum Eligibility & Prerequisite Check",
        "category": "Academic Prerequisite",
        "severity": "MEDIUM",
        "regulatory_reference": "AICTE APH 2024-27 Minimum Entry Qualifications [DEMO SPECIFICATION - Unverified Clause Citation]",
        "description": "Flags records where entry qualification credentials require secondary verification against qualifying board databases. Proposed rule specification; not executed in runtime intake parser [DEMO SPECIFICATION].",
        "status": "ACTIVE",
        "implementation_status": "DEMO_SPECIFICATION",
        "reference_status": "DEMO_REFERENCE",
    },
    {
        "code": "R05_STATE_QUOTA_ANOMALY",
        "title": "Approved Quota Allocation Adherence",
        "category": "Quota & Equity Compliance",
        "severity": "LOW",
        "regulatory_reference": "State Admission Regulatory Committee (SARC) Guidelines [DEMO SPECIFICATION - Unverified State Parameters]",
        "description": "Monitors ratio of State Merit vs Institutional/Management quota enrolments against sanctioned limits. Proposed rule specification; not executed in runtime intake parser [DEMO SPECIFICATION].",
        "status": "ACTIVE",
        "implementation_status": "DEMO_SPECIFICATION",
        "reference_status": "DEMO_REFERENCE",
    },
    {
        "code": "R06_SUPERNUMERARY_CAP_EXCEEDED",
        "title": "Supernumerary Seat Ceiling (TFWS/EWS/PMSSS)",
        "category": "Quota & Equity Compliance",
        "severity": "MEDIUM",
        "regulatory_reference": "AICTE Tuition Fee Waiver Scheme (TFWS) Guidelines [Statutory 5% Cap Verified; Engine Integration DEMO SPECIFICATION]",
        "description": "Validates that supernumerary allocations strictly conform to statutory ceilings (e.g. 5% TFWS). Proposed rule specification; not executed in runtime intake parser [DEMO SPECIFICATION].",
        "status": "ACTIVE",
        "implementation_status": "DEMO_SPECIFICATION",
        "reference_status": "DEMO_REFERENCE",
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
