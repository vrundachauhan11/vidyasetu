"""Comprehensive tests for Authentication, Session Tokens, and Role-Based Access Control (RBAC)."""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.modules.auth.security import create_access_token, decode_access_token, DEMO_PERSONAS


VALID_CSV = """student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Test Candidate,DEMO-APAAR-2026-AUT7890,2007-01-15,Male,General,State Merit Quota,ENR-AUTH-TEST-001,2025-08-16,B.Tech Computer Science and Engineering
"""


@pytest.mark.asyncio
async def test_unauthenticated_access_to_me_returns_401(unauthenticated_client):
    """1. Accessing /api/auth/me without an Authorization header returns 401."""
    resp = await unauthenticated_client.get("/api/auth/me")
    assert resp.status_code == 401
    assert "Authentication required" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_unauthenticated_intake_upload_returns_401(unauthenticated_client):
    """2. Accessing intake upload without authentication returns 401."""
    files = {"file": ("test.csv", VALID_CSV.encode("utf-8"), "text/csv")}
    resp = await unauthenticated_client.post("/api/intake/upload", files=files)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_review_decision_returns_401(unauthenticated_client):
    """3. Submitting review decision without authentication returns 401."""
    resp = await unauthenticated_client.post(
        "/api/review/nonexistent-sig/decision",
        json={"decision": "RESOLVED_ACCEPTED", "reviewer_notes": "Attempt without login"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_rule_configuration_returns_401(unauthenticated_client):
    """4. Configuring rules without authentication returns 401."""
    resp = await unauthenticated_client.patch(
        "/api/rules/R01_SANCTIONED_INTAKE_EXCEEDED/configuration",
        json={"severity": "MEDIUM"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_tampered_or_malformed_token_returns_401(unauthenticated_client):
    """5. Supplying a forged or modified token returns 401."""
    valid_token = create_access_token("usr_01", "test@vidyasetu.local", "REGULATOR_AICTE")
    tampered_token = valid_token[:-4] + "ffff"
    headers = {"Authorization": f"Bearer {tampered_token}"}
    resp = await unauthenticated_client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 401
    assert "Authentication failed" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_login_success_for_all_demo_roles(unauthenticated_client):
    """6. Every demo persona can log in with their documented demo credentials."""
    for role, persona in DEMO_PERSONAS.items():
        resp = await unauthenticated_client.post(
            "/api/auth/login",
            json={"email": persona["email"], "password": persona["demo_password"]},
        )
        assert resp.status_code == 200, f"Login failed for role {role}: {resp.text}"
        data = resp.json()
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["role"] == role
        assert data["user"]["email"] == persona["email"]

        # Verify issued token works to fetch /api/auth/me
        token = data["token"]
        auth_header = {"Authorization": f"Bearer {token}"}
        me_resp = await unauthenticated_client.get("/api/auth/me", headers=auth_header)
        assert me_resp.status_code == 200
        assert me_resp.json()["role"] == role


@pytest.mark.asyncio
async def test_login_with_quick_role_selector(unauthenticated_client):
    """7. 1-Click demo role selector returns valid token without typing password."""
    resp = await unauthenticated_client.post(
        "/api/auth/login",
        json={"role": "INSTITUTION_ADMIN"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "INSTITUTION_ADMIN"
    assert data["token"] is not None


@pytest.mark.asyncio
async def test_login_invalid_password_returns_401(unauthenticated_client):
    """8. Submitting wrong demo password returns 401 with descriptive error."""
    resp = await unauthenticated_client.post(
        "/api/auth/login",
        json={"email": "admin@apex-tech.edu", "password": "WrongPassword!2026"},
    )
    assert resp.status_code == 401
    assert "Invalid demo credentials" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_rbac_intake_upload_allowed_for_institution_admin():
    """9. Institution Admin can upload CSV batches."""
    admin_token = create_access_token("usr_inst_01", "admin@apex-tech.edu", "INSTITUTION_ADMIN")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {admin_token}"},
    ) as ac:
        files = {"file": ("admin_intake.csv", VALID_CSV.encode("utf-8"), "text/csv")}
        resp = await ac.post("/api/intake/upload", files=files)
        assert resp.status_code == 200
        assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_rbac_intake_upload_forbidden_for_compliance_reviewer():
    """10. Compliance Reviewer is forbidden from uploading intake batches (returns 403)."""
    reviewer_token = create_access_token("usr_rev_01", "reviewer.desk@vidyasetu.local", "COMPLIANCE_REVIEWER")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {reviewer_token}"},
    ) as ac:
        files = {"file": ("rev_intake.csv", VALID_CSV.encode("utf-8"), "text/csv")}
        resp = await ac.post("/api/intake/upload", files=files)
        assert resp.status_code == 403
        assert "not authorized" in resp.json().get("detail", "").lower()
        assert "COMPLIANCE_REVIEWER" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_rbac_review_decision_forbidden_for_institution_admin():
    """11. Institution Admin is forbidden from adjudicating review decisions (returns 403)."""
    admin_token = create_access_token("usr_inst_01", "admin@apex-tech.edu", "INSTITUTION_ADMIN")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {admin_token}"},
    ) as ac:
        resp = await ac.post(
            "/api/review/any-signal-id/decision",
            json={"decision": "RESOLVED_ACCEPTED", "reviewer_notes": "Admin trying to resolve"},
        )
        assert resp.status_code == 403
        assert "not authorized" in resp.json().get("detail", "").lower()
        assert "INSTITUTION_ADMIN" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_rbac_rule_configuration_allowed_for_regulator():
    """12. AICTE Regulator can configure and update rules."""
    regulator_token = create_access_token("usr_reg_01", "compliance.officer@aicte-gov.in", "REGULATOR_AICTE")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {regulator_token}"},
    ) as ac:
        resp = await ac.patch(
            "/api/rules/R01_SANCTIONED_INTAKE_EXCEEDED/configuration",
            json={"severity": "HIGH", "status": "ACTIVE"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_rbac_rule_configuration_forbidden_for_compliance_reviewer():
    """13. Compliance Reviewer is forbidden from modifying configured rules (returns 403)."""
    reviewer_token = create_access_token("usr_rev_01", "reviewer.desk@vidyasetu.local", "COMPLIANCE_REVIEWER")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {reviewer_token}"},
    ) as ac:
        resp = await ac.patch(
            "/api/rules/R01_SANCTIONED_INTAKE_EXCEEDED/configuration",
            json={"severity": "LOW"},
        )
        assert resp.status_code == 403
        assert "not authorized" in resp.json().get("detail", "").lower()
        assert "COMPLIANCE_REVIEWER" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_rbac_rule_configuration_forbidden_for_institution_admin():
    """14. Institution Admin is forbidden from modifying configured rules (returns 403)."""
    admin_token = create_access_token("usr_inst_01", "admin@apex-tech.edu", "INSTITUTION_ADMIN")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {admin_token}"},
    ) as ac:
        resp = await ac.patch(
            "/api/rules/R01_SANCTIONED_INTAKE_EXCEEDED/configuration",
            json={"severity": "LOW"},
        )
        assert resp.status_code == 403
        assert "not authorized" in resp.json().get("detail", "").lower()
        assert "INSTITUTION_ADMIN" in resp.json().get("detail", "")


@pytest.mark.asyncio
async def test_permission_elevation_denied_when_switching_role():
    """15. Changing role selector after login CANNOT elevate permissions to higher roles (returns 403)."""
    admin_token = create_access_token("usr_inst_01", "admin@apex-tech.edu", "INSTITUTION_ADMIN")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {admin_token}"},
    ) as ac:
        # Admin attempting to switch to Regulator
        resp = await ac.post("/api/auth/switch-role", json={"role": "REGULATOR_AICTE"})
        assert resp.status_code == 403
        assert "permission elevation denied" in resp.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_role_scoping_allowed_for_regulator():
    """16. Higher-privileged regulator can scope view down to institutional preview."""
    reg_token = create_access_token("usr_reg_01", "compliance.officer@aicte-gov.in", "REGULATOR_AICTE")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {reg_token}"},
    ) as ac:
        resp = await ac.post("/api/auth/switch-role", json={"role": "INSTITUTION_ADMIN"})
        assert resp.status_code == 200
        assert resp.json()["user"]["role"] == "INSTITUTION_ADMIN"


@pytest.mark.asyncio
async def test_logout_terminates_session():
    """17. Logout endpoint responds with session termination message."""
    token = create_access_token("usr_inst_01", "admin@apex-tech.edu", "INSTITUTION_ADMIN")
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        resp = await ac.post("/api/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["success"] is True
        assert "logged out" in resp.json().get("message", "").lower()
