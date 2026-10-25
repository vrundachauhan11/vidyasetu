"""Student Records & Versioning Module."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import StudentEnrolment, Institution, ProgrammeApproval

router = APIRouter(prefix="/students", tags=["Student Records & Versioning"])


@router.get("")
async def list_students(
    apaar_status: Optional[str] = Query(None),
    integrity_status: Optional[str] = Query(None),
    institution_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List synthetic student enrolments with regulatory state flags."""
    stmt = (
        select(StudentEnrolment)
        .options(
            selectinload(StudentEnrolment.institution),
            selectinload(StudentEnrolment.programme),
            selectinload(StudentEnrolment.signals),
        )
        .order_by(StudentEnrolment.created_at.desc())
    )

    if apaar_status:
        stmt = stmt.where(StudentEnrolment.apaar_status == apaar_status)
    if integrity_status:
        stmt = stmt.where(StudentEnrolment.integrity_status == integrity_status)
    if institution_id:
        stmt = stmt.where(StudentEnrolment.institution_id == institution_id)

    result = await db.execute(stmt)
    records = result.scalars().all()

    if search:
        s_lower = search.lower()
        records = [
            r for r in records
            if s_lower in r.student_name.lower()
            or (r.apaar_id and s_lower in r.apaar_id.lower())
            or (r.enrolment_number and s_lower in r.enrolment_number.lower())
        ]

    return {
        "success": True,
        "demo_mode": True,
        "disclaimer": "DEMO DATA ONLY - All student identities are synthetic.",
        "count": len(records),
        "data": [
            {
                "id": r.id,
                "student_name": r.student_name,
                "apaar_id": r.apaar_id,
                "apaar_status": r.apaar_status,
                "dob": r.dob,
                "gender": r.gender,
                "category": r.category,
                "quota": r.quota,
                "enrolment_number": r.enrolment_number,
                "admission_date": r.admission_date,
                "integrity_status": r.integrity_status,
                "version": r.version,
                "institution_name": r.institution.name if r.institution else "N/A",
                "programme_name": r.programme.programme_name if r.programme else "N/A",
                "signals": [
                    {
                        "id": s.id,
                        "rule_code": s.rule_code,
                        "severity": s.severity,
                        "finding_summary": s.finding_summary,
                        "explanation": s.explanation,
                        "review_status": s.review_status,
                        "reviewer_decision": s.reviewer_decision,
                        "reviewer_notes": s.reviewer_notes,
                        "reviewed_at": s.reviewed_at.isoformat() if s.reviewed_at else None,
                        "created_at": s.created_at.isoformat() if s.created_at else None,
                    }
                    for s in sorted(r.signals, key=lambda x: str(x.created_at or ""), reverse=True)
                ],
            }
            for r in records
        ],
    }


@router.get("/{student_id}")
async def get_student(student_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full detail and audit history of a specific synthetic student enrolment."""
    stmt = (
        select(StudentEnrolment)
        .options(
            selectinload(StudentEnrolment.institution),
            selectinload(StudentEnrolment.programme),
            selectinload(StudentEnrolment.signals),
        )
        .where(StudentEnrolment.id == student_id)
    )
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    return {
        "success": True,
        "demo_mode": True,
        "data": {
            "id": student.id,
            "student_name": student.student_name,
            "apaar_id": student.apaar_id,
            "apaar_status": student.apaar_status,
            "dob": student.dob,
            "gender": student.gender,
            "category": student.category,
            "quota": student.quota,
            "enrolment_number": student.enrolment_number,
            "admission_date": student.admission_date,
            "integrity_status": student.integrity_status,
            "version": student.version,
            "institution": {
                "id": student.institution.id if student.institution else "",
                "name": student.institution.name if student.institution else "N/A",
                "aicte_id": student.institution.aicte_id if student.institution else "N/A",
            },
            "programme": {
                "id": student.programme.id if student.programme else "",
                "programme_name": student.programme.programme_name if student.programme else "N/A",
                "sanctioned_intake": student.programme.sanctioned_intake if student.programme else 0,
            },
            "signals": [
                {
                    "id": s.id,
                    "rule_code": s.rule_code,
                    "severity": s.severity,
                    "finding_summary": s.finding_summary,
                    "explanation": s.explanation,
                    "review_status": s.review_status,
                    "reviewer_decision": s.reviewer_decision,
                    "reviewer_notes": s.reviewer_notes,
                    "reviewed_at": s.reviewed_at.isoformat() if s.reviewed_at else None,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sorted(student.signals, key=lambda x: str(x.created_at or ""), reverse=True)
            ],
        },
    }
