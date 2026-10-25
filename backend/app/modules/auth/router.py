"""Authentication & Role-Based Access Control (RBAC) Module."""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


class UserProfile(BaseModel):
    user_id: str
    email: str
    name: str
    role: str  # REGULATOR_AICTE, INSTITUTION_ADMIN, COMPLIANCE_REVIEWER, AUDITOR
    institution_id: str = "DEMO-AICTE-1-0091823"
    permissions: List[str]


DEMO_USERS = {
    "REGULATOR_AICTE": UserProfile(
        user_id="usr_reg_01",
        email="compliance.officer@aicte-gov.in",
        name="Dr. V. K. Adhikari (AICTE Council Reviewer)",
        role="REGULATOR_AICTE",
        institution_id="ALL",
        permissions=["view_all_institutions", "manage_rules", "triage_signals", "view_audit_trail", "export_reports"],
    ),
    "INSTITUTION_ADMIN": UserProfile(
        user_id="usr_inst_01",
        email="admin@apex-tech.edu",
        name="Prof. Sunita Rao (Registrar, Apex Tech)",
        role="INSTITUTION_ADMIN",
        institution_id="DEMO-AICTE-1-0091823",
        permissions=["upload_csv_batch", "view_own_students", "respond_to_signals", "view_own_audit"],
    ),
    "COMPLIANCE_REVIEWER": UserProfile(
        user_id="usr_rev_01",
        email="reviewer.desk@vidyasetu.local",
        name="Er. Rajesh Pillai (Independent Compliance Evaluator)",
        role="COMPLIANCE_REVIEWER",
        institution_id="ALL",
        permissions=["review_signals", "resolve_flags", "request_evidence"],
    ),
    "AUDITOR": UserProfile(
        user_id="usr_aud_01",
        email="auditor@cag-scrutiny.gov.in",
        name="Smt. Neelam Sengupta (Auditor General)",
        role="AUDITOR",
        institution_id="ALL",
        permissions=["view_audit_trail", "verify_hashes", "generate_compliance_audit"],
    ),
}

current_active_role = "REGULATOR_AICTE"


class SwitchRoleRequest(BaseModel):
    role: str


@router.get("/me", response_model=UserProfile)
async def get_current_user():
    """Retrieve current active authenticated user and RBAC profile."""
    return DEMO_USERS.get(current_active_role, DEMO_USERS["REGULATOR_AICTE"])


@router.post("/switch-role", response_model=UserProfile)
async def switch_demo_role(payload: SwitchRoleRequest):
    """Switch active demo role for demonstration of role-specific workflows."""
    global current_active_role
    if payload.role in DEMO_USERS:
        current_active_role = payload.role
    return DEMO_USERS.get(current_active_role, DEMO_USERS["REGULATOR_AICTE"])


@router.get("/roles")
async def list_available_roles():
    """List available demo roles."""
    return [
        {"role": "REGULATOR_AICTE", "title": "AICTE Council Regulator", "description": "National council-level view with policy oversight and rule management"},
        {"role": "INSTITUTION_ADMIN", "title": "Institution Registrar", "description": "Campus intake upload, APAAR sync, and response to review signals"},
        {"role": "COMPLIANCE_REVIEWER", "title": "Independent Compliance Reviewer", "description": "Triage desk for resolving integrity flags and evidence review"},
        {"role": "AUDITOR", "title": "Regulatory Auditor", "description": "Read-only scrutiny of cryptographic audit trail and compliance history"},
    ]
