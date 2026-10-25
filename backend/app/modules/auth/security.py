"""Security, token generation, and RBAC authorization dependencies for VidyaSetu.
Note: This is an explainable prototype security implementation designed for hackathon demonstration.
All demo credentials and tokens are synthetic and clearly demarcated.
"""
import hmac
import hashlib
import json
import base64
import time
from typing import Optional, Dict, Any, List
from fastapi import Header, HTTPException, status, Depends
from pydantic import BaseModel

from app.config import settings
from app.logging_config import logger


class UserProfile(BaseModel):
    user_id: str
    email: str
    name: str
    role: str  # REGULATOR_AICTE, INSTITUTION_ADMIN, COMPLIANCE_REVIEWER, AUDITOR
    institution_id: str = "DEMO-AICTE-1-0091823"
    permissions: List[str]


# Pre-configured Synthetic Demo Personas for SIH Hackathon Evaluation
DEMO_PERSONAS: Dict[str, Dict[str, Any]] = {
    "INSTITUTION_ADMIN": {
        "user_id": "usr_inst_01",
        "email": "admin@apex-tech.edu",
        "demo_password": "DemoAdmin@2026",
        "name": "Prof. Sunita Rao (Registrar, Apex Tech)",
        "role": "INSTITUTION_ADMIN",
        "role_title": "Institution Registrar",
        "institution_id": "DEMO-AICTE-1-0091823",
        "institution_name": "Apex Institute of Technology",
        "description": "Campus intake upload, APAAR sync roster, and response to review signals",
        "permissions": [
            "upload_csv_batch",
            "view_own_students",
            "respond_to_signals",
            "view_own_audit",
            "view_institution_profile",
        ],
    },
    "COMPLIANCE_REVIEWER": {
        "user_id": "usr_rev_01",
        "email": "reviewer.desk@vidyasetu.local",
        "demo_password": "DemoReviewer@2026",
        "name": "Er. Rajesh Pillai (Independent Compliance Evaluator)",
        "role": "COMPLIANCE_REVIEWER",
        "role_title": "Compliance Reviewer",
        "institution_id": "ALL",
        "institution_name": "AICTE Standing Review Panel",
        "description": "Triage desk for resolving integrity flags, reviewing evidence and overruling signals",
        "permissions": [
            "review_signals",
            "resolve_flags",
            "request_evidence",
            "triage_signals",
            "view_audit_trail",
        ],
    },
    "REGULATOR_AICTE": {
        "user_id": "usr_reg_01",
        "email": "compliance.officer@aicte-gov.in",
        "demo_password": "DemoRegulator@2026",
        "name": "Dr. V. K. Adhikari (AICTE Council Reviewer)",
        "role": "REGULATOR_AICTE",
        "role_title": "AICTE Council Regulator",
        "institution_id": "ALL",
        "institution_name": "All India Council for Technical Education",
        "description": "National council-level view with policy oversight, rule management and full supervisory clearance",
        "permissions": [
            "view_all_institutions",
            "manage_rules",
            "triage_signals",
            "view_audit_trail",
            "export_reports",
            "upload_csv_batch",
            "review_signals",
            "resolve_flags",
        ],
    },
    "AUDITOR": {
        "user_id": "usr_aud_01",
        "email": "auditor@cag-scrutiny.gov.in",
        "demo_password": "DemoAuditor@2026",
        "name": "Smt. Neelam Sengupta (Auditor General)",
        "role": "AUDITOR",
        "role_title": "Regulatory Auditor",
        "institution_id": "ALL",
        "institution_name": "CAG Scrutiny Cell",
        "description": "Read-only scrutiny of cryptographic audit trail, SHA-256 tamper logs and compliance history",
        "permissions": [
            "view_audit_trail",
            "verify_hashes",
            "generate_compliance_audit",
            "export_reports",
        ],
    },
}

# Lookup by email
DEMO_PERSONAS_BY_EMAIL = {data["email"].lower(): data for data in DEMO_PERSONAS.values()}


def create_access_token(user_id: str, email: str, role: str, expires_in_minutes: Optional[int] = None) -> str:
    """Create a tamper-evident HMAC-SHA256 signed bearer token."""
    expire_minutes = expires_in_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    exp_timestamp = int(time.time()) + (expire_minutes * 60)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": exp_timestamp,
        "iat": int(time.time()),
        "iss": "VidyaSetu-Prototype-Auth",
    }
    raw_json = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    encoded_payload = base64.urlsafe_b64encode(raw_json).decode("utf-8").rstrip("=")

    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{encoded_payload}.{signature}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify signature and expiration of an access token."""
    try:
        if not token or "." not in token:
            return None
        parts = token.split(".")
        if len(parts) != 2:
            return None
        encoded_payload, signature = parts

        expected_sig = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            encoded_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            return None

        # Re-pad base64
        rem = len(encoded_payload) % 4
        padded = encoded_payload + ("=" * (4 - rem) if rem else "")
        payload_data = json.loads(base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8"))

        if payload_data.get("exp", 0) < time.time():
            return None

        return payload_data
    except Exception as exc:
        logger.debug(f"Token decoding failed: {exc}")
        return None


def get_user_profile(role: str) -> UserProfile:
    """Construct UserProfile object for a recognized role."""
    data = DEMO_PERSONAS.get(role, DEMO_PERSONAS["REGULATOR_AICTE"])
    return UserProfile(
        user_id=data["user_id"],
        email=data["email"],
        name=data["name"],
        role=data["role"],
        institution_id=data["institution_id"],
        permissions=data["permissions"],
    )


async def get_current_user(authorization: Optional[str] = Header(None)) -> UserProfile:
    """Dependency: Extract and validate Bearer token from request header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: No Bearer token provided in Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed: Session token is expired, malformed, or has an invalid signature.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role = payload.get("role")
    if not role or role not in DEMO_PERSONAS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: Unknown role '{role}' in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return get_user_profile(role)


def require_roles(*allowed_roles: str):
    """Dependency factory: Enforce that the authenticated user possesses one of the allowed roles."""
    async def role_checker(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access Denied: Role '{current_user.role}' is not authorized to perform this operation. "
                    f"Required role(s): {', '.join(allowed_roles)}."
                ),
            )
        return current_user

    return role_checker


def require_permissions(*required_permissions: str):
    """Dependency factory: Enforce that the authenticated user possesses all specified permissions."""
    async def permission_checker(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
        for perm in required_permissions:
            if perm not in current_user.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access Denied: User role '{current_user.role}' lacks required permission: '{perm}'.",
                )
        return current_user

    return permission_checker
