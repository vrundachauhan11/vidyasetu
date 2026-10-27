"""Regression tests for CSV Data Intake & Validation."""
import io
import pytest
from unittest.mock import patch


VALID_SYNTHETIC_CSV = """student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Aaditya Nambiar,DEMO-APAAR-2026-904990,2007-01-15,Male,General,State Merit Quota,ENR-TEST-REG-001,2025-08-16,B.Tech Computer Science and Engineering
Bhavna Deshmukh,DEMO-APAAR-2026-904993,2006-11-20,Female,OBC-NCL,State Merit Quota,ENR-TEST-REG-002,2025-08-16,B.Tech Computer Science and Engineering
"""


@pytest.mark.asyncio
async def test_successful_csv_upload(client):
    """1. Successful CSV upload with valid schema and synthetic records."""
    files = {
        "file": ("valid_intake.csv", VALID_SYNTHETIC_CSV.encode("utf-8"), "text/csv")
    }
    response = await client.post("/api/intake/upload", files=files)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["success"] is True
    assert "batch_reference" in data
    assert data["summary"]["total_records"] == 2
    assert data["summary"]["valid_records"] == 1  # 904990 ends with 0 -> VERIFIED
    assert data["summary"]["flagged_records"] == 1  # 904993 ends with 3 -> PENDING_VERIFICATION


@pytest.mark.asyncio
async def test_invalid_or_missing_headers(client):
    """2. CSV with missing required columns returns 422 with descriptive error."""
    bad_csv = """student_name,dob,gender,enrolment_number
Rahul Sen,2007-02-10,Male,ENR-MISSING-001
"""
    files = {
        "file": ("missing_cols.csv", bad_csv.encode("utf-8"), "text/csv")
    }
    response = await client.post("/api/intake/upload", files=files)
    assert response.status_code == 422
    data = response.json()
    # Check that missing columns are reported
    error_msg = data.get("detail", "")
    assert "Missing required column" in error_msg
    assert "apaar_id" in error_msg


@pytest.mark.asyncio
async def test_malformed_csv_input(client):
    """3. Malformed CSV input: non-csv extension, empty content, and header-only files."""
    # 3a. Non-csv extension
    files_txt = {"file": ("students.txt", b"some text", "text/plain")}
    resp_txt = await client.post("/api/intake/upload", files=files_txt)
    assert resp_txt.status_code == 400
    assert "Only CSV format" in resp_txt.json().get("detail", "")

    # 3b. Empty file
    files_empty = {"file": ("empty.csv", b"", "text/csv")}
    resp_empty = await client.post("/api/intake/upload", files=files_empty)
    assert resp_empty.status_code == 400
    assert "empty" in resp_empty.json().get("detail", "").lower()

    # 3c. Header only with no data rows
    header_only = "student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name\n"
    files_hdr = {"file": ("header_only.csv", header_only.encode("utf-8"), "text/csv")}
    resp_hdr = await client.post("/api/intake/upload", files=files_hdr)
    assert resp_hdr.status_code == 422
    assert "no data rows" in resp_hdr.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_database_failure_during_upload(client):
    """4. Database failure during upload rolls back transaction and returns HTTP 500."""
    with patch("sqlalchemy.ext.asyncio.AsyncSession.commit") as mock_commit:
        mock_commit.side_effect = RuntimeError("Simulated Database I/O Failure")

        files = {
            "file": ("db_fail.csv", VALID_SYNTHETIC_CSV.encode("utf-8"), "text/csv")
        }
        response = await client.post("/api/intake/upload", files=files)
        assert response.status_code == 500
        data = response.json()
        assert "Database transaction failure" in data.get("detail", "")


@pytest.mark.asyncio
async def test_duplicate_record_handling(client):
    """5. Duplicate record handling:
       a) Re-uploading existing enrolment number increments version (v1 -> v2) without crashing.
       b) Intra-batch duplicate enrolment is flagged with R03 signal.
    """
    import uuid
    test_enr = f"ENR-VTEST-{uuid.uuid4().hex[:6].upper()}"

    # 5a. Inter-batch re-upload (versioning)
    initial_csv = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Chetan Bhagat,DEMO-APAAR-2026-904880,2007-05-10,Male,General,State Merit Quota,{test_enr},2025-08-16,B.Tech Computer Science and Engineering
"""
    files1 = {"file": ("batch1.csv", initial_csv.encode("utf-8"), "text/csv")}
    resp1 = await client.post("/api/intake/upload", files=files1)
    assert resp1.status_code == 200

    # Query student to confirm version 1
    stud_resp1 = await client.get(f"/api/students?search={test_enr}")
    assert stud_resp1.status_code == 200
    records1 = stud_resp1.json()["data"]
    assert len(records1) == 1
    assert records1[0]["version"] == 1

    # Upload second batch with same enrolment number (e.g. updated quota/name)
    updated_csv = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Chetan Bhagat,DEMO-APAAR-2026-904880,2007-05-10,Male,General,Management Quota,{test_enr},2025-08-16,B.Tech Computer Science and Engineering
"""
    files2 = {"file": ("batch2.csv", updated_csv.encode("utf-8"), "text/csv")}
    resp2 = await client.post("/api/intake/upload", files=files2)
    assert resp2.status_code == 200, f"Expected 200 on re-upload, got {resp2.status_code}: {resp2.text}"

    # Query student to confirm version incremented to 2
    stud_resp2 = await client.get(f"/api/students?search={test_enr}")
    records2 = stud_resp2.json()["data"]
    assert len(records2) == 1
    assert records2[0]["version"] == 2
    assert records2[0]["quota"] == "Management Quota"

    # 5b. Intra-batch duplicate enrolment
    intra_enr = f"ENR-INTRADUP-{uuid.uuid4().hex[:6].upper()}"
    intra_dup_csv = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Student Alpha,DEMO-APAAR-2026-904770,2007-01-01,Female,General,State Merit Quota,{intra_enr},2025-08-16,B.Tech Computer Science and Engineering
Student Beta,DEMO-APAAR-2026-904772,2007-01-02,Male,General,State Merit Quota,{intra_enr},2025-08-16,B.Tech Computer Science and Engineering
"""
    files_dup = {"file": ("intra_dup.csv", intra_dup_csv.encode("utf-8"), "text/csv")}
    resp_dup = await client.post("/api/intake/upload", files=files_dup)
    assert resp_dup.status_code == 200
    dup_data = resp_dup.json()
    assert dup_data["summary"]["total_records"] == 2
    assert dup_data["summary"]["flagged_records"] >= 1


@pytest.mark.asyncio
async def test_persistence_of_intake_batch_and_students(client):
    """6. Correct persistence of intake batch, student records, and cryptographic audit trail."""
    unique_enr = "ENR-PERSIST-CHECK-001"
    unique_apaar = "DEMO-APAAR-2026-904660"
    persist_csv = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Deepika Padukone,{unique_apaar},2007-04-12,Female,General,State Merit Quota,{unique_enr},2025-08-16,B.Tech Computer Science and Engineering
"""
    files = {"file": ("persist_test.csv", persist_csv.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200
    batch_ref = resp.json()["batch_reference"]

    # Verify batch is in batches list
    batches_resp = await client.get("/api/intake/batches")
    assert batches_resp.status_code == 200
    batch_refs = [b["batch_reference"] for b in batches_resp.json()["data"]]
    assert batch_ref in batch_refs

    # Verify student record is persisted
    students_resp = await client.get(f"/api/students?search={unique_enr}")
    assert students_resp.status_code == 200
    students = students_resp.json()["data"]
    assert len(students) >= 1
    assert students[0]["enrolment_number"] == unique_enr
    assert students[0]["apaar_id"] == unique_apaar

    # Verify audit log is recorded
    audit_resp = await client.get("/api/audit/logs")
    assert audit_resp.status_code == 200
    actions = [l["action"] for l in audit_resp.json()["data"]]
    assert "BATCH_CSV_UPLOAD" in actions


@pytest.mark.asyncio
async def test_canonical_csv_schema_upload(client):
    """7. Valid canonical CSV upload with exact 9 canonical headers."""
    import uuid
    suffix = uuid.uuid4().hex[:6].upper()
    canonical_csv = f"""student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Ananya Canonical,DEMO-APAAR-2026-904550,2007-02-14,Female,General,State Merit Quota,ENR-CANON-{suffix},2025-08-16,B.Tech Computer Science and Engineering
"""
    files = {"file": ("canonical_valid.csv", canonical_csv.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["success"] is True
    assert body["summary"]["total_records"] == 1


@pytest.mark.asyncio
async def test_utf8_bom_and_whitespace_and_case_in_headers(client):
    """8. Header parsing safely handles UTF-8 BOM, whitespace around headers, and case variations."""
    import uuid
    suffix = uuid.uuid4().hex[:6].upper()
    # Headers have leading/trailing whitespace, mixed casing, and spaces
    messy_header_csv = (
        "  Student_Name  , apaar_id , DOB , Gender , Category , Quota , Enrolment_Number , Admission_Date , Programme_Name \n"
        f"Karan Rawat,DEMO-APAAR-2026-904551,2007-03-20,Male,General,State Merit Quota,ENR-BOM-{suffix},2025-08-16,B.Tech Computer Science and Engineering\n"
    )
    # Encode with UTF-8 BOM prefix (\xef\xbb\xbf)
    bom_bytes = b"\xef\xbb\xbf" + messy_header_csv.encode("utf-8")
    files = {"file": ("bom_messy_headers.csv", bom_bytes, "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 200, f"Expected 200 with BOM and whitespace, got {resp.status_code}: {resp.text}"
    body = resp.json()
    assert body["success"] is True
    assert body["summary"]["total_records"] == 1


@pytest.mark.asyncio
async def test_missing_required_columns_reporting(client):
    """9. Missing required columns produces 422 listing genuinely missing columns."""
    # Omit category, quota, and programme_name
    partial_csv = """student_name,apaar_id,dob,gender,enrolment_number,admission_date
Sunil Gavaskar,DEMO-APAAR-2026-904552,2006-07-10,Male,ENR-MISS-999,2025-08-16
"""
    files = {"file": ("missing_fields.csv", partial_csv.encode("utf-8"), "text/csv")}
    resp = await client.post("/api/intake/upload", files=files)
    assert resp.status_code == 422
    err_detail = resp.json().get("detail", "")
    assert "CSV schema mismatch. Missing required column(s):" in err_detail
    assert "category" in err_detail
    assert "quota" in err_detail
    assert "programme_name" in err_detail
    # Ensure columns that WERE provided are NOT in the missing list
    assert "student_name" not in err_detail.replace("Missing required column(s):", "")
    assert "apaar_id" not in err_detail.replace("Missing required column(s):", "")
    assert "dob" not in err_detail.replace("Missing required column(s):", "")
    assert "gender" not in err_detail.replace("Missing required column(s):", "")
    assert "enrolment_number" not in err_detail.replace("Missing required column(s):", "")
    assert "admission_date" not in err_detail.replace("Missing required column(s):", "")


@pytest.mark.asyncio
async def test_template_headers_match_backend_expectations(client):
    """10. Downloadable template headers match the backend canonical schema exactly."""
    import csv
    import io
    from app.modules.intake.router import CANONICAL_COLUMNS

    resp = await client.get("/api/intake/sample-csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
    assert 'attachment; filename="vidyasetu_intake_template.csv"' in resp.headers.get("content-disposition", "")

    reader = csv.reader(io.StringIO(resp.text))
    headers = next(reader)
    clean_headers = [h.strip() for h in headers]
    assert clean_headers == CANONICAL_COLUMNS, f"Template headers {clean_headers} != Canonical {CANONICAL_COLUMNS}"


@pytest.mark.asyncio
async def test_prebuilt_synthetic_csv_passes_validation(client):
    """11. Pre-built synthetic CSV downloaded from template endpoint passes validation without schema error."""
    resp_template = await client.get("/api/intake/sample-csv")
    assert resp_template.status_code == 200
    sample_csv_text = resp_template.text

    files = {
        "file": ("Synthetic_Institutional_Intake_Round2.csv", sample_csv_text.encode("utf-8"), "text/csv")
    }
    resp_upload = await client.post("/api/intake/upload", files=files)
    assert resp_upload.status_code == 200, f"Expected 200 for prebuilt CSV, got {resp_upload.status_code}: {resp_upload.text}"
    data = resp_upload.json()
    assert data["success"] is True
    assert data["summary"]["total_records"] == 5

