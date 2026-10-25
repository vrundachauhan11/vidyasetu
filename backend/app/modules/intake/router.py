"""Data Intake & Batch Ingestion Module."""
import csv
import io
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import IntakeBatch, Institution, ProgrammeApproval, StudentEnrolment, IntegritySignal, AuditLog
from app.seed.demo_data import generate_tamper_hash

router = APIRouter(prefix="/intake", tags=["Data Intake & Validation"])

SAMPLE_CSV_CONTENT = """student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Kavya Krishnan,DEMO-APAAR-2026-904140,2007-03-10,Female,General,State Merit Quota,ENR-2025-CSE-005,2025-08-16,B.Tech Computer Science and Engineering
Devansh Singhania,DEMO-APAAR-2026-904141,2006-12-04,Male,General,Management Quota,ENR-2025-CSE-006,2025-08-16,B.Tech Computer Science and Engineering
Meera Joshi,DEMO-APAAR-2026-904142,2007-07-22,Female,OBC-NCL,State Merit Quota,ENR-2025-CSE-007,2025-08-17,B.Tech Computer Science and Engineering
Tarun Balakrishnan,DEMO-APAAR-2026-904143,2006-05-18,Male,SC,State Merit Quota,ENR-2025-CSE-008,2025-08-17,B.Tech Computer Science and Engineering
Simran Kaur,DEMO-APAAR-2026-904144,2007-09-01,Female,EWS,State Merit Quota,ENR-2025-CSE-009,2025-08-18,B.Tech Computer Science and Engineering
"""


@router.get("/sample-csv", response_class=PlainTextResponse)
async def get_sample_csv():
    """Download a valid synthetic demo CSV template."""
    return SAMPLE_CSV_CONTENT


@router.get("/batches")
async def list_intake_batches(db: AsyncSession = Depends(get_db)):
    """List recent data intake batches."""
    stmt = select(IntakeBatch).order_by(IntakeBatch.uploaded_at.desc())
    res = await db.execute(stmt)
    batches = res.scalars().all()
    return {
        "success": True,
        "demo_mode": True,
        "data": [
            {
                "id": b.id,
                "batch_reference": b.batch_reference,
                "academic_year": b.academic_year,
                "filename": b.filename,
                "total_records": b.total_records,
                "valid_records": b.valid_records,
                "flagged_records": b.flagged_records,
                "status": b.status,
                "uploaded_at": b.uploaded_at.isoformat() if b.uploaded_at else "",
            }
            for b in batches
        ],
    }


@router.post("/upload")
async def upload_intake_csv(
    file: UploadFile = File(...),
    institution_id: str = "DEMO-AICTE-1-0091823",
    db: AsyncSession = Depends(get_db),
):
    """Upload and validate synthetic student roster CSV.
    Executes schema checks, deterministic rules, and creates intake batch.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV format is accepted for data intake.")

    contents = await file.read()
    text = contents.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))

    required_fields = ["student_name", "apaar_id", "dob", "gender", "category", "quota", "enrolment_number"]
    if not reader.fieldnames or not all(f in reader.fieldnames for f in required_fields):
        raise HTTPException(
            status_code=422,
            detail=f"CSV schema mismatch. Missing one or more required columns: {required_fields}",
        )

    # Find institution
    inst_res = await db.execute(select(Institution).where(Institution.aicte_id == institution_id))
    inst = inst_res.scalar_one_or_none()
    if not inst:
        # Fallback to first institution
        fallback_res = await db.execute(select(Institution).limit(1))
        inst = fallback_res.scalar_one_or_none()

    if not inst:
        raise HTTPException(status_code=400, detail="No institution found to associate intake batch with.")

    # Find default programme
    prog_res = await db.execute(
        select(ProgrammeApproval).where(ProgrammeApproval.institution_id == inst.id).limit(1)
    )
    prog = prog_res.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    batch_ref = f"BATCH-{now.strftime('%Y%m%d-%H%M%S')}"

    valid_count = 0
    flagged_count = 0
    records_processed = 0

    batch = IntakeBatch(
        id=str(uuid.uuid4()),
        institution_id=inst.id,
        batch_reference=batch_ref,
        academic_year="2025-26",
        filename=file.filename,
        total_records=0,
        valid_records=0,
        flagged_records=0,
        status="PROCESSED",
        uploaded_at=now,
    )
    db.add(batch)
    await db.flush()

    for row in reader:
        records_processed += 1
        name = row.get("student_name", "").strip()
        apaar = row.get("apaar_id", "").strip()
        enr = row.get("enrolment_number", "").strip()

        # Simulated APAAR verification outcome:
        # If apaar starts with DEMO-APAAR and ends with even number: VERIFIED
        # If ends with 3: PENDING
        # If empty or ends with 9: MISMATCH
        if not apaar:
            apaar_status = "UNAVAILABLE"
            integrity_status = "FLAGGED_FOR_REVIEW"
            flagged_count += 1
        elif apaar.endswith("3"):
            apaar_status = "PENDING_VERIFICATION"
            integrity_status = "FLAGGED_FOR_REVIEW"
            flagged_count += 1
        elif apaar.endswith("9"):
            apaar_status = "MISMATCH"
            integrity_status = "FLAGGED_FOR_REVIEW"
            flagged_count += 1
        else:
            apaar_status = "VERIFIED"
            integrity_status = "CLEARED"
            valid_count += 1

        student = StudentEnrolment(
            id=str(uuid.uuid4()),
            institution_id=inst.id,
            programme_id=prog.id if prog else inst.id,
            student_name=f"{name} [DEMO]",
            apaar_id=apaar,
            apaar_status=apaar_status,
            dob=row.get("dob", "2007-01-01"),
            gender=row.get("gender", "Female"),
            category=row.get("category", "General"),
            quota=row.get("quota", "State Merit Quota"),
            enrolment_number=enr or f"ENR-{uuid.uuid4().hex[:6].upper()}",
            admission_date=row.get("admission_date", now.strftime("%Y-%m-%d")),
            integrity_status=integrity_status,
            version=1,
            is_latest=True,
            created_at=now,
        )
        db.add(student)
        await db.flush()

        if integrity_status == "FLAGGED_FOR_REVIEW":
            sig = IntegritySignal(
                id=str(uuid.uuid4()),
                student_id=student.id,
                rule_code="R02_APAAR_MOCK_DISCREPANCY",
                severity="MEDIUM",
                finding_summary=f"Automated verification signal: APAAR status is {apaar_status}",
                explanation=f"Simulated verification adapter returned status '{apaar_status}' for synthetic identifier '{apaar}'. Requires human reviewer verification.",
                review_status="PENDING",
                created_at=now,
            )
            db.add(sig)

    batch.total_records = records_processed
    batch.valid_records = valid_count
    batch.flagged_records = flagged_count
    batch.status = "REVIEW_REQUIRED" if flagged_count > 0 else "COMPLETED"

    # Add audit log entry
    thash = generate_tamper_hash("institution_admin@apex.edu", "BATCH_CSV_UPLOAD", f"intake_batches/{batch_ref}", now.isoformat())
    audit_log = AuditLog(
        id=str(uuid.uuid4()),
        timestamp=now,
        actor="institution_admin@apex.edu",
        role="INSTITUTION_ADMIN",
        action="BATCH_CSV_UPLOAD",
        resource=f"intake_batches/{batch_ref}",
        details_json=f'{{"filename": "{file.filename}", "total": {records_processed}, "valid": {valid_count}, "flagged": {flagged_count}}}',
        tamper_hash=thash,
    )
    db.add(audit_log)

    await db.commit()

    return {
        "success": True,
        "demo_mode": True,
        "batch_reference": batch_ref,
        "summary": {
            "total_records": records_processed,
            "valid_records": valid_count,
            "flagged_records": flagged_count,
            "status": batch.status,
        },
        "message": f"Successfully processed intake batch {batch_ref} with {records_processed} synthetic student records.",
    }
