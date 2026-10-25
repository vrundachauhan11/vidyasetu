"""APAAR Integration Adapter Module.
All operations in this module communicate with a DETERMINISTIC SIMULATION ADAPTER.
Does NOT connect to live DigiLocker/APAAR production registries.
"""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import StudentEnrolment
from app.config import settings

router = APIRouter(prefix="/apaar", tags=["APAAR Validation Adapter (MOCK)"])


class ApaarLookupRequest(BaseModel):
    apaar_id: str
    student_name: str
    dob: Optional[str] = None


@router.get("/status")
async def get_apaar_adapter_status():
    """Retrieve simulated APAAR adapter connectivity and security parameters."""
    return {
        "success": True,
        "mode": "SIMULATION_MOCK",
        "is_mock": True,
        "disclaimer": "SIMULATED APAAR ADAPTER - No live government connectivity is established.",
        "adapter_config": {
            "endpoint_uri": "mock://apaar.digilocker.simulation.local/v1/verify",
            "latency_ms": settings.APAAR_MOCK_LATENCY_MS,
            "deterministic_seed": "VIDYASETU_MOCK_2026",
            "supported_protocols": ["OAuth2-PKCE-Mock", "Signed-JWT-Mock"],
            "privacy_notice": "In compliance with DPDP Act 2023, student identifiers are checked under explicit educational regulatory purpose limitation.",
        },
    }


@router.get("/records")
async def get_apaar_validation_records(db: AsyncSession = Depends(get_db)):
    """Fetch students with their distinct APAAR validation stage details."""
    stmt = select(StudentEnrolment).order_by(StudentEnrolment.created_at.desc())
    res = await db.execute(stmt)
    students = res.scalars().all()

    items = []
    for s in students:
        # Generate simulated handshake telemetry
        if s.apaar_status == "VERIFIED":
            handshake = {
                "mock_response_code": "200_MATCH_CONFIRMED",
                "identity_score": 100,
                "token_id": f"TOK-APAAR-{s.apaar_id[-6:] if s.apaar_id else '0000'}",
                "remarks": "Identity record match confirmed by simulated registry.",
            }
        elif s.apaar_status == "PENDING_VERIFICATION":
            handshake = {
                "mock_response_code": "202_ACCEPTED_IN_QUEUE",
                "identity_score": None,
                "token_id": None,
                "remarks": "Asynchronous batch verification pending acknowledgment. Note: Pending status is an operational signal and does NOT imply fraud.",
            }
        elif s.apaar_status == "MISMATCH":
            handshake = {
                "mock_response_code": "409_IDENTITY_DISCREPANCY",
                "identity_score": 88,
                "token_id": f"TOK-REV-{s.apaar_id[-6:] if s.apaar_id else '0000'}",
                "remarks": "Spelling variation identified between institutional roster and registry.",
            }
        else:
            handshake = {
                "mock_response_code": "404_ID_NOT_FOUND",
                "identity_score": 0,
                "token_id": None,
                "remarks": "No APAAR identifier submitted with record.",
            }

        items.append({
            "student_id": s.id,
            "student_name": s.student_name,
            "apaar_id": s.apaar_id or "Not Provided",
            "apaar_status": s.apaar_status,
            "integrity_status": s.integrity_status,
            "handshake": handshake,
        })

    return {
        "success": True,
        "is_mock": True,
        "disclaimer": "DEMO DATA ONLY - External APAAR check is simulated.",
        "count": len(items),
        "data": items,
    }


@router.post("/lookup")
async def simulate_apaar_lookup(payload: ApaarLookupRequest):
    """Simulate single APAAR ID identity verification handshake."""
    apaar_clean = payload.apaar_id.strip()
    name_clean = payload.student_name.strip()

    if not apaar_clean:
        return {
            "success": False,
            "is_mock": True,
            "status": "UNAVAILABLE",
            "message": "No APAAR ID provided.",
        }

    if apaar_clean.endswith("3"):
        return {
            "success": True,
            "is_mock": True,
            "status": "PENDING_VERIFICATION",
            "score": None,
            "message": "Handshake submitted to simulated registry; verification pending acknowledgment. (Signal, not fraud).",
        }
    elif apaar_clean.endswith("9"):
        return {
            "success": True,
            "is_mock": True,
            "status": "MISMATCH",
            "score": 85,
            "message": f"Simulated registry returns minor name discrepancy for '{name_clean}'. Review signal flagged.",
        }
    else:
        return {
            "success": True,
            "is_mock": True,
            "status": "VERIFIED",
            "score": 100,
            "token": f"MOCK-APAAR-TOK-{apaar_clean[-4:]}",
            "message": "Simulated APAAR identity verified successfully.",
        }
