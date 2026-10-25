"""Institutions & Programme Approvals Module."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import Institution, ProgrammeApproval

router = APIRouter(prefix="/institutions", tags=["Institutions & Approvals"])


@router.get("")
async def list_institutions(db: AsyncSession = Depends(get_db)):
    """List all AICTE-approved institutions with programme breakdown."""
    stmt = select(Institution).options(selectinload(Institution.programmes)).order_by(Institution.name)
    result = await db.execute(stmt)
    institutions = result.scalars().all()

    return {
        "success": True,
        "demo_mode": True,
        "disclaimer": "DEMO DATA ONLY - Synthetic Institutions for Evaluation",
        "data": [
            {
                "id": inst.id,
                "aicte_id": inst.aicte_id,
                "name": inst.name,
                "state": inst.state,
                "district": inst.district,
                "institution_type": inst.institution_type,
                "approval_status": inst.approval_status,
                "programmes": [
                    {
                        "id": p.id,
                        "programme_name": p.programme_name,
                        "degree_level": p.degree_level,
                        "academic_year": p.academic_year,
                        "sanctioned_intake": p.sanctioned_intake,
                        "approved_quota_details": p.approved_quota_details,
                    }
                    for p in inst.programmes
                ],
            }
            for inst in institutions
        ],
    }


@router.get("/{institution_id}")
async def get_institution(institution_id: str, db: AsyncSession = Depends(get_db)):
    """Get single institution details."""
    stmt = (
        select(Institution)
        .options(selectinload(Institution.programmes))
        .where(Institution.id == institution_id)
    )
    result = await db.execute(stmt)
    inst = result.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    return {
        "success": True,
        "demo_mode": True,
        "data": {
            "id": inst.id,
            "aicte_id": inst.aicte_id,
            "name": inst.name,
            "state": inst.state,
            "district": inst.district,
            "institution_type": inst.institution_type,
            "approval_status": inst.approval_status,
            "programmes": [
                {
                    "id": p.id,
                    "programme_name": p.programme_name,
                    "degree_level": p.degree_level,
                    "academic_year": p.academic_year,
                    "sanctioned_intake": p.sanctioned_intake,
                    "approved_quota_details": p.approved_quota_details,
                }
                for p in inst.programmes
            ],
        },
    }
