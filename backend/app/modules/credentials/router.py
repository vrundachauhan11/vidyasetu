"""Credentials & Public Verification Module."""
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import StudentEnrolment

router = APIRouter(prefix="/credentials", tags=["Credentials & Verification"])


@router.get("/verify/{query_key}")
async def verify_credential(query_key: str, db: AsyncSession = Depends(get_db)):
    """Public tamper-evident verification of student enrolment certificate / credential by Enrolment Number or APAAR ID."""
    clean_key = query_key.strip()
    stmt = (
        select(StudentEnrolment)
        .options(selectinload(StudentEnrolment.institution), selectinload(StudentEnrolment.programme))
        .where(
            (StudentEnrolment.enrolment_number == clean_key)
            | (StudentEnrolment.apaar_id == clean_key)
            | (StudentEnrolment.id == clean_key)
        )
    )
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()

    if not student:
        raise HTTPException(
            status_code=404,
            detail=f"No verified enrolment credential found for identifier '{clean_key}'.",
        )

    # Compute deterministic credential verification fingerprint
    raw_payload = f"{student.enrolment_number}|{student.apaar_id}|{student.institution.name}|{student.admission_date}|vidyasetu-root-anchor"
    fingerprint = hashlib.sha256(raw_payload.encode()).hexdigest()

    return {
        "success": True,
        "demo_mode": True,
        "is_mock": True,
        "disclaimer": "DEMO VERIFICATION - Educational credential verification simulated.",
        "verified": True,
        "credential": {
            "student_name": student.student_name,
            "enrolment_number": student.enrolment_number,
            "apaar_id": student.apaar_id or "Not Provided",
            "apaar_status": student.apaar_status,
            "institution_name": student.institution.name if student.institution else "N/A",
            "aicte_id": student.institution.aicte_id if student.institution else "N/A",
            "programme": student.programme.programme_name if student.programme else "N/A",
            "admission_date": student.admission_date,
            "integrity_standing": "IN GOOD STANDING" if student.integrity_status in ["CLEARED", "RESOLVED"] else "UNDER REGULATORY REVIEW",
            "cryptographic_fingerprint": fingerprint,
            "verification_timestamp": student.created_at.isoformat() if student.created_at else "",
        },
    }
