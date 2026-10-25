"""Automated regression tests for signal deduplication, rule semantics, and reviewer decision stability."""
import uuid
import pytest
from app.modules.intake.deduplicate import deduplicate_existing_signals
from app.models import IntegritySignal, StudentEnrolment
from sqlalchemy import select


@pytest.mark.asyncio
async def test_signal_deduplication_on_repeated_upload(client):
    """Uploading the same CSV multiple times does not produce duplicate active signals."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    test_enr = f"ENR-DEDUP-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-880003"  # ends with 3 -> PENDING_VERIFICATION

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Kavya Deshmukh,{test_apaar},2006-09-12,Female,General,State Merit Quota,{test_enr},2025-08-16,B.Tech Computer Science and Engineering
"""

    # 1. First upload
    files1 = {"file": ("upload1.csv", csv_data.encode("utf-8"), "text/csv")}
    resp1 = await client.post("/api/intake/upload", files=files1)
    assert resp1.status_code == 200

    # Verify student has exactly 1 signal
    res1 = await client.get(f"/api/students?search={test_enr}")
    assert res1.status_code == 200
    st1 = res1.json()["data"][0]
    assert len(st1["signals"]) == 1
    assert st1["signals"][0]["rule_code"] == "R02_APAAR_PENDING_ACKNOWLEDGEMENT"
    assert st1["signals"][0]["review_status"] == "PENDING"
    assert st1["signals"][0]["severity"] == "LOW"

    # 2. Re-upload 3 more times
    for i in range(2, 5):
        files_i = {"file": (f"upload{i}.csv", csv_data.encode("utf-8"), "text/csv")}
        resp_i = await client.post("/api/intake/upload", files=files_i)
        assert resp_i.status_code == 200

    # Verify student STILL has exactly 1 signal (no duplicates)
    res_final = await client.get(f"/api/students?search={test_enr}")
    assert res_final.status_code == 200
    st_final = res_final.json()["data"][0]
    assert len(st_final["signals"]) == 1
    assert st_final["signals"][0]["rule_code"] == "R02_APAAR_PENDING_ACKNOWLEDGEMENT"
    assert st_final["signals"][0]["review_status"] == "PENDING"
    assert st_final["version"] == 4


@pytest.mark.asyncio
async def test_resolved_findings_remain_resolved_after_reupload(client):
    """A human reviewer resolution is preserved and does not revert to FLAGGED or create duplicates on re-upload."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    test_enr = f"ENR-RESOLVE-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-770003"  # ends with 3 -> PENDING

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Tarun TestCandidate,{test_apaar},2006-05-18,Male,SC,State Merit Quota,{test_enr},2025-08-17,B.Tech Computer Science and Engineering
"""

    # Initial upload
    files = {"file": ("initial.csv", csv_data.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200

    # Get student and signal id
    res = await client.get(f"/api/students?search={test_enr}")
    student = res.json()["data"][0]
    assert student["integrity_status"] == "FLAGGED_FOR_REVIEW"
    assert len(student["signals"]) == 1
    sig_id = student["signals"][0]["id"]

    # Submit reviewer resolution
    review_payload = {
        "decision": "RESOLVED_ACCEPTED",
        "reviewer_notes": "Accepted institutional justification: APAAR pending adapter handshake.",
        "reviewer_role": "COMPLIANCE_REVIEWER",
        "reviewer_email": "compliance.desk@vidyasetu.local",
    }
    review_resp = await client.post(f"/api/review/{sig_id}/decision", json=review_payload)
    assert review_resp.status_code == 200

    # Verify student is now RESOLVED
    res_after_review = await client.get(f"/api/students?search={test_enr}")
    student_reviewed = res_after_review.json()["data"][0]
    assert student_reviewed["integrity_status"] == "RESOLVED"
    assert student_reviewed["signals"][0]["review_status"] == "RESOLVED_ACCEPTED"
    assert student_reviewed["signals"][0]["reviewer_decision"] == "RESOLVED_ACCEPTED"
    assert "Accepted institutional justification" in student_reviewed["signals"][0]["reviewer_notes"]

    # Re-upload the exact same CSV batch (simulating periodic intake or refresh)
    reupload_files = {"file": ("reupload.csv", csv_data.encode("utf-8"), "text/csv")}
    reupload_resp = await client.post("/api/intake/upload", files=reupload_files)
    assert reupload_resp.status_code == 200

    # Verify:
    # 1. Student integrity status is STILL RESOLVED (NOT flipped back to FLAGGED_FOR_REVIEW)
    # 2. No duplicate pending signal was added
    # 3. Reviewer decision and notes remain intact
    res_after_reupload = await client.get(f"/api/students?search={test_enr}")
    student_final = res_after_reupload.json()["data"][0]
    assert student_final["integrity_status"] == "RESOLVED"
    assert len(student_final["signals"]) == 1
    assert student_final["signals"][0]["review_status"] == "RESOLVED_ACCEPTED"
    assert student_final["signals"][0]["reviewer_decision"] == "RESOLVED_ACCEPTED"
    assert "Accepted institutional justification" in student_final["signals"][0]["reviewer_notes"]


@pytest.mark.asyncio
async def test_rule_semantics_pending_is_low_severity_and_not_discrepancy(client):
    """A PENDING APAAR status emits R02_APAAR_PENDING_ACKNOWLEDGEMENT with LOW severity, not discrepancy."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    test_enr = f"ENR-SEM-PEND-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-660003"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Pooja Semantics,{test_apaar},2007-02-15,Female,General,State Merit Quota,{test_enr},2025-08-16,B.Tech Computer Science and Engineering
"""
    files = {"file": ("pending.csv", csv_data.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200

    res = await client.get(f"/api/students?search={test_enr}")
    student = res.json()["data"][0]
    assert student["apaar_status"] == "PENDING_VERIFICATION"
    sig = student["signals"][0]
    assert sig["rule_code"] == "R02_APAAR_PENDING_ACKNOWLEDGEMENT"
    assert sig["severity"] == "LOW"
    assert "discrepancy" not in sig["finding_summary"].lower()


@pytest.mark.asyncio
async def test_rule_semantics_missing_apaar_emits_unavailable(client):
    """An empty APAAR status emits R02_APAAR_UNAVAILABLE_IN_ROSTER with LOW severity."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    test_enr = f"ENR-SEM-NOAP-{unique_suffix}"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Roster Candidate,,2007-03-10,Female,General,State Merit Quota,{test_enr},2025-08-16,B.Tech Computer Science and Engineering
"""
    files = {"file": ("missing_apaar.csv", csv_data.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200

    res = await client.get(f"/api/students?search={test_enr}")
    student = res.json()["data"][0]
    assert student["apaar_status"] == "UNAVAILABLE"
    sig = student["signals"][0]
    assert sig["rule_code"] == "R02_APAAR_UNAVAILABLE_IN_ROSTER"
    assert sig["severity"] == "LOW"


@pytest.mark.asyncio
async def test_rule_semantics_mismatch_emits_name_discrepancy(client):
    """An APAAR ending with 9 emits R02_APAAR_NAME_DISCREPANCY with MEDIUM severity."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    test_enr = f"ENR-SEM-MIS-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-550009"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Aarav Verma,{test_apaar},2006-08-30,Male,EWS,Management Quota,{test_enr},2025-08-16,B.Tech Computer Science and Engineering
"""
    files = {"file": ("mismatch.csv", csv_data.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200

    res = await client.get(f"/api/students?search={test_enr}")
    student = res.json()["data"][0]
    assert student["apaar_status"] == "MISMATCH"
    sig = student["signals"][0]
    assert sig["rule_code"] == "R02_APAAR_NAME_DISCREPANCY"
    assert sig["severity"] == "MEDIUM"
