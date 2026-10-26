"""Comprehensive automated tests for Rule Registry execution, statutory scenarios, and deduplication."""
import uuid
import pytest
from app.modules.intake.deduplicate import deduplicate_existing_signals
from app.models import IntegritySignal, StudentEnrolment, ProgrammeApproval
from sqlalchemy import select


@pytest.mark.asyncio
async def test_signal_deduplication_on_repeated_upload(client, create_isolated_programme):
    """Uploading the same CSV multiple times does not produce duplicate active signals."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE Dedup {unique_suffix}"
    await create_isolated_programme(prog_name, sanctioned_intake=50)

    test_enr = f"ENR-DEDUP-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-DED{unique_suffix[:3]}3"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Kavya Deshmukh,{test_apaar},2006-09-12,Female,General,State Merit Quota,{test_enr},2025-08-16,{prog_name}
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
async def test_resolved_findings_remain_resolved_after_reupload(client, create_isolated_programme):
    """A human reviewer resolution is preserved and does not revert to FLAGGED or create duplicates on re-upload."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE Resolve {unique_suffix}"
    await create_isolated_programme(prog_name, sanctioned_intake=50)

    test_enr = f"ENR-RESOLVE-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-RES{unique_suffix[:3]}3"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Tarun TestCandidate,{test_apaar},2006-05-18,Male,SC,State Merit Quota,{test_enr},2025-08-17,{prog_name}
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


@pytest.mark.asyncio
async def test_scenario_enrolment_within_approved_intake(client, create_isolated_programme):
    """Scenario 1: Student enrolment with verified APAAR within sanctioned intake is CLEARED with 0 signals."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE Clean {unique_suffix}"
    await create_isolated_programme(prog_name, sanctioned_intake=50)

    test_enr = f"ENR-CLEAN-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-CLN{unique_suffix[:3]}0"  # ends with 0 -> VERIFIED

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Valid Candidate,{test_apaar},2007-04-12,Female,General,State Merit Quota,{test_enr},2025-08-16,{prog_name}
"""
    files = {"file": ("clean.csv", csv_data.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200

    res = await client.get(f"/api/students?search={test_enr}")
    student = res.json()["data"][0]
    assert student["integrity_status"] == "CLEARED"
    assert student["apaar_status"] == "VERIFIED"
    assert len(student["signals"]) == 0


@pytest.mark.asyncio
async def test_scenario_enrolment_exceeding_configured_intake(client, create_isolated_programme):
    """Scenario 2: Enrolment exceeding programme approved capacity triggers R01_SANCTIONED_INTAKE_EXCEEDED."""
    suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE LowCap {suffix}"
    # Dedicated isolated programme configured with sanctioned intake limit of exactly 1 seat
    await create_isolated_programme(prog_name, sanctioned_intake=1)

    enr1 = f"ENR-CAP1-{suffix}"
    enr2 = f"ENR-CAP2-{suffix}"
    apaar1 = f"DEMO-APAAR-2026-CP1{suffix[:3]}0"
    apaar2 = f"DEMO-APAAR-2026-CP2{suffix[:3]}0"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Candidate Within Capacity,{apaar1},2007-01-01,Female,General,State Merit Quota,{enr1},2025-08-16,{prog_name}
Candidate Exceeding Intake,{apaar2},2007-01-02,Male,General,State Merit Quota,{enr2},2025-08-16,{prog_name}
"""
    files = {"file": ("capacity_test.csv", csv_data.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200

    # Candidate 1 (sequence 1 <= 1) is cleared
    res1 = await client.get(f"/api/students?search={enr1}")
    st1 = res1.json()["data"][0]
    assert st1["integrity_status"] == "CLEARED"
    assert len(st1["signals"]) == 0

    # Candidate 2 (sequence 2 > 1) is flagged for exceeding approved capacity
    res2 = await client.get(f"/api/students?search={enr2}")
    st2 = res2.json()["data"][0]
    assert st2["integrity_status"] == "FLAGGED_FOR_REVIEW"
    assert any(s["rule_code"] == "R01_SANCTIONED_INTAKE_EXCEEDED" for s in st2["signals"])

    # Verify R01 exists in registered rules with verified statutory reference
    rules_resp = await client.get("/api/rules")
    r01_rule = next(r for r in rules_resp.json()["data"] if r["code"] == "R01_SANCTIONED_INTAKE_EXCEEDED")
    assert r01_rule["severity"] == "HIGH"
    assert r01_rule["implementation_status"] == "OPERATIONAL"
    assert r01_rule["reference_status"] == "VERIFIED_STATUTORY"
    assert "DEMO CONFIGURATION" in r01_rule["regulatory_reference"] or "AICTE Act 1987" in r01_rule["regulatory_reference"]


@pytest.mark.asyncio
async def test_scenario_duplicate_enrolment_number(client, create_isolated_programme):
    """Scenario 3: Duplicate enrolment number in batch triggers R03_DUPLICATE_CONCURRENT_ENROLMENT."""
    suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE DupEnr {suffix}"
    await create_isolated_programme(prog_name, sanctioned_intake=50)

    dup_enr = f"ENR-DUP-{suffix}"
    apaar1 = f"DEMO-APAAR-2026-D1{suffix[:3]}0"
    apaar2 = f"DEMO-APAAR-2026-D2{suffix[:3]}0"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Candidate First,{apaar1},2007-01-01,Female,General,State Merit Quota,{dup_enr},2025-08-16,{prog_name}
Candidate Second,{apaar2},2007-01-02,Male,General,State Merit Quota,{dup_enr},2025-08-16,{prog_name}
"""
    files = {"file": ("dup_enr.csv", csv_data.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"]["flagged_records"] >= 1

    # Verify duplicate is flagged with R03
    res = await client.get(f"/api/students?search={dup_enr}")
    students = res.json()["data"]
    assert len(students) >= 1
    flagged = [s for s in students if s["integrity_status"] == "FLAGGED_FOR_REVIEW"]
    assert len(flagged) >= 1
    assert any(sig["rule_code"] == "R03_DUPLICATE_CONCURRENT_ENROLMENT" for sig in flagged[0]["signals"])


@pytest.mark.asyncio
async def test_scenario_duplicate_synthetic_apaar(client, create_isolated_programme):
    """Scenario 4: Duplicate synthetic APAAR identifier across different enrolment numbers triggers R03."""
    suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE DupApaar {suffix}"
    await create_isolated_programme(prog_name, sanctioned_intake=50)

    shared_apaar = f"DEMO-APAAR-2026-SHR{suffix[:3]}0"
    enr1 = f"ENR-SHR1-{suffix}"
    enr2 = f"ENR-SHR2-{suffix}"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Student One,{shared_apaar},2007-02-01,Female,General,State Merit Quota,{enr1},2025-08-16,{prog_name}
Student Two,{shared_apaar},2007-02-02,Male,General,State Merit Quota,{enr2},2025-08-16,{prog_name}
"""
    files = {"file": ("dup_apaar.csv", csv_data.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200

    # The second student sharing the APAAR ID is flagged with R03_DUPLICATE_CONCURRENT_ENROLMENT
    res2 = await client.get(f"/api/students?search={enr2}")
    st2 = res2.json()["data"][0]
    assert st2["integrity_status"] == "FLAGGED_FOR_REVIEW"
    sig_codes = [s["rule_code"] for s in st2["signals"]]
    assert "R03_DUPLICATE_CONCURRENT_ENROLMENT" in sig_codes


@pytest.mark.asyncio
async def test_rule_semantics_pending_is_low_severity_and_not_discrepancy(client, create_isolated_programme):
    """Scenario 5: PENDING APAAR status emits R02_APAAR_PENDING_ACKNOWLEDGEMENT with LOW severity."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE SemPending {unique_suffix}"
    await create_isolated_programme(prog_name, sanctioned_intake=50)

    test_enr = f"ENR-SEM-PEND-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-PND{unique_suffix[:3]}3"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Pooja Semantics,{test_apaar},2007-02-15,Female,General,State Merit Quota,{test_enr},2025-08-16,{prog_name}
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
async def test_rule_semantics_missing_apaar_emits_unavailable(client, create_isolated_programme):
    """Scenario 6: Empty/Missing APAAR status emits R02_APAAR_UNAVAILABLE_IN_ROSTER with LOW severity."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE SemMissing {unique_suffix}"
    await create_isolated_programme(prog_name, sanctioned_intake=50)

    test_enr = f"ENR-SEM-NOAP-{unique_suffix}"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Roster Candidate,,2007-03-10,Female,General,State Merit Quota,{test_enr},2025-08-16,{prog_name}
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
    assert "fraud" not in sig["explanation"].lower() or "not proof of fraud" in sig["explanation"].lower()


@pytest.mark.asyncio
async def test_rule_semantics_mismatch_emits_name_discrepancy(client, create_isolated_programme):
    """Scenario 7: APAAR ending with 9 emits R02_APAAR_NAME_DISCREPANCY with MEDIUM severity."""
    unique_suffix = uuid.uuid4().hex[:6].upper()
    prog_name = f"B.Tech CSE SemMismatch {unique_suffix}"
    await create_isolated_programme(prog_name, sanctioned_intake=50)

    test_enr = f"ENR-SEM-MIS-{unique_suffix}"
    test_apaar = f"DEMO-APAAR-2026-MSM{unique_suffix[:3]}9"

    csv_data = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Aarav Verma,{test_apaar},2006-08-30,Male,EWS,Management Quota,{test_enr},2025-08-16,{prog_name}
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


@pytest.mark.asyncio
async def test_rule_registry_statutory_transparency(client):
    """Verify that all rules explicitly declare implementation_status and reference_status."""
    resp = await client.get("/api/rules")
    assert resp.status_code == 200
    rules = resp.json()["data"]
    assert len(rules) >= 6

    for r in rules:
        assert "implementation_status" in r
        assert r["implementation_status"] in ("OPERATIONAL", "DEMO_SPECIFICATION")
        assert "reference_status" in r
        assert r["reference_status"] in ("VERIFIED_STATUTORY", "DEMO_REFERENCE")
        # Ensure unverified parameters are flagged with DEMO CONFIGURATION
        if r["reference_status"] == "DEMO_REFERENCE" or "DEMO" in r["regulatory_reference"]:
            assert "DEMO" in r["regulatory_reference"] or "DEMO" in r["description"]
