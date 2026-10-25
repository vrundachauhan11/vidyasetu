"""Consent & Purpose Limitation Module (DPDP Act 2023 Alignment)."""
from fastapi import APIRouter

router = APIRouter(prefix="/consent", tags=["Consent & Purpose Checks"])


@router.get("/policies")
async def get_consent_policies():
    """Retrieve statutory purpose limitation notices and consent protocols under DPDP Act 2023."""
    return {
        "success": True,
        "demo_mode": True,
        "framework": "Digital Personal Data Protection (DPDP) Act 2023 & AICTE Regulatory Framework",
        "purpose_specification": "Processing of educational enrolment data is strictly restricted to verifying sanctioned intake ceilings, eliminating duplicate concurrent state quotas, and institutional regulatory compliance.",
        "policies": [
            {
                "purpose_code": "PURPOSE_ENROLMENT_INTEGRITY",
                "description": "Validation against approved AICTE intake capacity",
                "consent_required": "Statutory Regulatory Function (Section 7 DPDP Act)",
                "retention_period": "Duration of academic degree + 3 statutory audit years",
            },
            {
                "purpose_code": "PURPOSE_APAAR_IDENTITY_HANDSHAKE",
                "description": "Cross-verification with Academic Bank of Credits / APAAR",
                "consent_required": "Student / Guardian Consent collected during admission intake",
                "retention_period": "Immediate tokenization; raw PII masked in transit and logs",
            },
            {
                "purpose_code": "PURPOSE_CRYPTOGRAPHIC_AUDIT",
                "description": "Append-only SHA-256 tamper logs for regulatory oversight",
                "consent_required": "Statutory Governance Obligation",
                "retention_period": "7 years immutable audit trail",
            },
        ],
    }
