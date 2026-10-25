"""Evidence & Human Reviewer Workflow Module."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import IntegritySignal, StudentEnrolment, AuditLog
from app.seed.demo_data import generate_tamper_hash

router = APIRouter(prefix="/review", tags=["Evidence & Reviewer Workflow"])


class ReviewDecisionRequest(BaseModel):
    decision: str  # RESOLVED_ACCEPTED, RESOLVED_OVERRULED, DOCUMENT_VERIFIED
    reviewer_notes: str
    reviewer_role: str = "COMPLIANCE_REVIEWER"
    reviewer_email: str = "reviewer.desk@vidyasetu.local"


@router.get("/queue")
async def get_review_queue(db: AsyncSession = Depends(get_db)):
    """Fetch pending signals requiring human reviewer triage."""
    stmt = (
        select(IntegritySignal, StudentEnrolment.student_name, StudentEnrolment.enrolment_number, StudentEnrolment.apaar_id)
        .join(StudentEnrolment, IntegritySignal.student_id == StudentEnrolment.id)
        .where(IntegritySignal.review_status == "PENDING")
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
                "created_at": sig.created_at.isoformat() if sig.created_at else "",
            }
            for sig, s_name, s_enr, s_apaar in rows
        ],
    }


@router.post("/{signal_id}/decision")
async def submit_review_decision(
    signal_id: str,
    payload: ReviewDecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Submit human reviewer decision, update record version, and log to cryptographic audit trail."""
    stmt = select(IntegritySignal).where(IntegritySignal.id == signal_id)
    result = await db.execute(stmt)
    sig = result.scalar_one_or_none()
    if not sig:
        raise HTTPException(status_code=404, detail="Integrity signal not found.")

    now = datetime.now(timezone.utc)
    sig.review_status = payload.decision
    sig.reviewer_decision = payload.decision
    sig.reviewer_notes = payload.reviewer_notes
    sig.reviewed_at = now

    # Also update student enrolment status
    student_stmt = select(StudentEnrolment).where(StudentEnrolment.id == sig.student_id)
    student_res = await db.execute(student_stmt)
    student = student_res.scalar_one_or_none()
    if student:
        student.integrity_status = "RESOLVED" if payload.decision.startswith("RESOLVED") else "DOCUMENT_VERIFIED"
        student.version += 1
        student.updated_at = now

    # Append to tamper-evident audit log
    thash = generate_tamper_hash(payload.reviewer_email, "SIGNAL_REVIEW_DECISION", f"integrity_signals/{signal_id}", now.isoformat())
    audit = AuditLog(
        id=str(uuid.uuid4()),
        timestamp=now,
        actor=payload.reviewer_email,
        role=payload.reviewer_role,
        action="SIGNAL_REVIEW_DECISION",
        resource=f"integrity_signals/{signal_id}",
        details_json=f'{{"signal_id": "{signal_id}", "decision": "{payload.decision}", "notes": "{payload.reviewer_notes}", "rule": "{sig.rule_code}"}}',
        tamper_hash=thash,
    )
    db.add(audit)

    await db.commit()

    return {
        "success": True,
        "demo_mode": True,
        "signal_id": signal_id,
        "decision": payload.decision,
        "tamper_hash": thash,
        "message": f"Review decision '{payload.decision}' recorded successfully and stamped to immutable audit log.",
    }
