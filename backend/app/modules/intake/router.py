"""Data Intake & Batch Ingestion Module."""
import csv
import io
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import IntakeBatch, Institution, ProgrammeApproval, StudentEnrolment, IntegritySignal, AuditLog
from app.seed.demo_data import generate_tamper_hash
from app.logging_config import logger
from app.modules.auth.security import UserProfile, require_roles

router = APIRouter(prefix="/intake", tags=["Data Intake & Validation"])

CANONICAL_COLUMNS: list[str] = [
    "student_name",
    "apaar_id",
    "dob",
    "gender",
    "category",
    "quota",
    "enrolment_number",
    "admission_date",
    "programme_name",
]

HEADER_ALIASES: dict[str, str] = {
    # student_name
    "student_name": "student_name",
    "studentname": "student_name",
    "student": "student_name",
    "name": "student_name",
    "candidate_name": "student_name",
    "candidatename": "student_name",
    "full_name": "student_name",
    "fullname": "student_name",
    # apaar_id
    "apaar_id": "apaar_id",
    "apaarid": "apaar_id",
    "apaar": "apaar_id",
    "apaar_number": "apaar_id",
    "apaarnumber": "apaar_id",
    "abc_id": "apaar_id",
    "abcid": "apaar_id",
    # dob
    "dob": "dob",
    "date_of_birth": "dob",
    "dateofbirth": "dob",
    "birth_date": "dob",
    "birthdate": "dob",
    # gender
    "gender": "gender",
    "sex": "gender",
    # category
    "category": "category",
    "social_category": "category",
    "socialcategory": "category",
    "caste_category": "category",
    "caste": "category",
    # quota
    "quota": "quota",
    "admission_quota": "quota",
    "admissionquota": "quota",
    "seat_quota": "quota",
    "seatquota": "quota",
    # enrolment_number
    "enrolment_number": "enrolment_number",
    "enrolmentnumber": "enrolment_number",
    "enrolment_no": "enrolment_number",
    "enrolmentno": "enrolment_number",
    "enrollment_number": "enrolment_number",
    "enrollmentnumber": "enrolment_number",
    "enrollment_no": "enrolment_number",
    "enrollmentno": "enrolment_number",
    "registration_number": "enrolment_number",
    "registrationnumber": "enrolment_number",
    "registration_no": "enrolment_number",
    "reg_number": "enrolment_number",
    "reg_no": "enrolment_number",
    "regno": "enrolment_number",
    "roll_number": "enrolment_number",
    "roll_no": "enrolment_number",
    "rollno": "enrolment_number",
    # admission_date
    "admission_date": "admission_date",
    "admissiondate": "admission_date",
    "date_of_admission": "admission_date",
    "dateofadmission": "admission_date",
    "doa": "admission_date",
    # programme_name
    "programme_name": "programme_name",
    "programmename": "programme_name",
    "programme": "programme_name",
    "program_name": "programme_name",
    "programname": "programme_name",
    "program": "programme_name",
    "branch": "programme_name",
    "course": "programme_name",
    "stream": "programme_name",
    "degree": "programme_name",
    # optional: academic_year
    "academic_year": "academic_year",
    "academicyear": "academic_year",
    "ay": "academic_year",
    "session": "academic_year",
}


def normalize_header(raw_header: str) -> str:
    """Normalize a raw header string by stripping BOM, trimming whitespace, lowercasing, and normalizing punctuation."""
    if not raw_header:
        return ""
    cleaned = raw_header.lstrip("\ufeff").strip()
    normalized = cleaned.lower().replace("-", "_").replace(" ", "_")
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return HEADER_ALIASES.get(normalized, normalized)


SAMPLE_CSV_CONTENT = """student_name,apaar_id,dob,gender,category,quota,enrolment_number,admission_date,programme_name
Kavya Krishnan,DEMO-APAAR-2026-904140,2007-03-10,Female,General,State Merit Quota,ENR-2025-CSE-005,2025-08-16,B.Tech Computer Science and Engineering
Devansh Singhania,DEMO-APAAR-2026-904141,2006-12-04,Male,General,Management Quota,ENR-2025-CSE-006,2025-08-16,B.Tech Computer Science and Engineering
Meera Joshi,DEMO-APAAR-2026-904142,2007-07-22,Female,OBC-NCL,State Merit Quota,ENR-2025-CSE-007,2025-08-17,B.Tech Computer Science and Engineering
Tarun Balakrishnan,DEMO-APAAR-2026-904143,2006-05-18,Male,SC,State Merit Quota,ENR-2025-CSE-008,2025-08-17,B.Tech Computer Science and Engineering
Simran Kaur,DEMO-APAAR-2026-904144,2007-09-01,Female,EWS,State Merit Quota,ENR-2025-CSE-009,2025-08-18,B.Tech Computer Science and Engineering
"""


@router.get("/sample-csv")
async def get_sample_csv():
    """Download the canonical synthetic demo CSV template."""
    return Response(
        content=SAMPLE_CSV_CONTENT,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="vidyasetu_intake_template.csv"'},
    )


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
    academic_year: str = "2025-26",
    db: AsyncSession = Depends(get_db),
    current_user: UserProfile = Depends(require_roles("INSTITUTION_ADMIN", "REGULATOR_AICTE")),
):
    """Upload and validate synthetic student roster CSV.
    Executes schema checks, deterministic rules, duplicate handling with record versioning, and creates intake batch.
    """
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV format is accepted for data intake.")

    try:
        contents = await file.read()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(exc)}")

    if not contents or len(contents.strip()) == 0:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")

    # 1. Safely decode input bytes handling UTF-8-BOM, UTF-8, and fallback encodings
    if contents.startswith(b"\xef\xbb\xbf"):
        contents = contents[3:]

    try:
        text = contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            text = contents.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = contents.decode("latin-1")
            except Exception:
                raise HTTPException(status_code=400, detail="Malformed CSV input: unable to decode text.")

    # Strip any residual BOM character
    text = text.lstrip("\ufeff")

    # 2. Parse CSV header
    string_io = io.StringIO(text)
    try:
        csv_reader = csv.reader(string_io)
        raw_headers = next(csv_reader, None)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Malformed CSV input: {str(exc)}")

    if not raw_headers or not any(h.strip() for h in raw_headers):
        raise HTTPException(status_code=422, detail="CSV file has no header row.")

    # 3. Normalize headers and map to canonical names
    col_to_canonical: dict[int, str] = {}
    col_to_original: dict[int, str] = {}
    normalized_headers_set: set[str] = set()

    for idx, raw_h in enumerate(raw_headers):
        cleaned_raw = raw_h.lstrip("\ufeff").strip()
        canon = normalize_header(raw_h)
        if canon:
            col_to_canonical[idx] = canon
            normalized_headers_set.add(canon)
        col_to_original[idx] = cleaned_raw

    # 4. Check for genuinely missing canonical required columns
    missing_fields = [col for col in CANONICAL_COLUMNS if col not in normalized_headers_set]
    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail=f"CSV schema mismatch. Missing required column(s): {', '.join(missing_fields)}",
        )

    # 5. Parse data rows safely without discarding optional columns
    rows: list[dict[str, str]] = []
    for raw_row in csv_reader:
        # Skip completely empty lines
        if not raw_row or not any(field.strip() for field in raw_row):
            continue
        row_dict: dict[str, str] = {}
        for idx, val in enumerate(raw_row):
            val_clean = val.strip() if isinstance(val, str) else str(val)
            canon_key = col_to_canonical.get(idx)
            if canon_key:
                row_dict[canon_key] = val_clean
            orig_key = col_to_original.get(idx, f"col_{idx}")
            if orig_key and orig_key not in row_dict:
                row_dict[orig_key] = val_clean
        rows.append(row_dict)

    if len(rows) == 0:
        raise HTTPException(status_code=422, detail="CSV contains headers but no data rows.")

    # Find institution
    inst_res = await db.execute(select(Institution).where(Institution.aicte_id == institution_id))
    inst = inst_res.scalar_one_or_none()
    if not inst:
        fallback_res = await db.execute(select(Institution).limit(1))
        inst = fallback_res.scalar_one_or_none()

    if not inst:
        raise HTTPException(status_code=400, detail="No institution found to associate intake batch with.")

    # Find all programmes for this institution for accurate matching
    prog_res = await db.execute(
        select(ProgrammeApproval).where(ProgrammeApproval.institution_id == inst.id)
    )
    all_progs = prog_res.scalars().all()
    default_prog = all_progs[0] if all_progs else None

    now = datetime.now(timezone.utc)
    batch_ref = f"BATCH-{now.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

    valid_count = 0
    flagged_count = 0
    records_processed = 0
    seen_enrolments_in_batch = set()
    seen_apaars_in_batch = set()

    # Pre-fetch existing active enrolment counts per programme to evaluate intake capacity limits
    prog_counts_res = await db.execute(
        select(StudentEnrolment.programme_id, func.count(StudentEnrolment.id))
        .where(StudentEnrolment.institution_id == inst.id)
        .group_by(StudentEnrolment.programme_id)
    )
    prog_enrolment_counts = {p_id: cnt for p_id, cnt in prog_counts_res.all() if p_id}

    try:
        batch = IntakeBatch(
            id=str(uuid.uuid4()),
            institution_id=inst.id,
            batch_reference=batch_ref,
            academic_year=academic_year or "2025-26",
            filename=file.filename,
            total_records=0,
            valid_records=0,
            flagged_records=0,
            status="PROCESSED",
            uploaded_at=now,
        )
        db.add(batch)
        await db.flush()

        for row in rows:
            records_processed += 1
            name = (row.get("student_name") or "").strip()
            apaar = (row.get("apaar_id") or "").strip()
            enr = (row.get("enrolment_number") or "").strip()
            prog_name_in_row = (row.get("programme_name") or "").strip()
            row_ay = (row.get("academic_year") or academic_year or "2025-26").strip()

            # Match programme by institution, programme name, and academic year
            matched_prog = default_prog
            if prog_name_in_row:
                for p in all_progs:
                    if p.programme_name.lower() == prog_name_in_row.lower() and p.academic_year == row_ay:
                        matched_prog = p
                        break
                else:
                    for p in all_progs:
                        if p.programme_name.lower() == prog_name_in_row.lower():
                            matched_prog = p
                            break

            # Validate basic row completeness
            if not name:
                name = f"Unnamed Candidate #{records_processed}"

            findings: list[tuple[str, str, str, str]] = []

            # 1. Simulated APAAR verification outcome:
            # - If apaar empty: UNAVAILABLE (operational data gap, NOT fraud) -> R02_APAAR_UNAVAILABLE_IN_ROSTER (LOW)
            # - If apaar ends with 3: PENDING_VERIFICATION (operational sync delay, NOT fraud) -> R02_APAAR_PENDING_ACKNOWLEDGEMENT (LOW)
            # - If apaar ends with 9: MISMATCH (spelling anomaly review flag) -> R02_APAAR_NAME_DISCREPANCY (MEDIUM)
            # - Otherwise: VERIFIED
            if not apaar:
                apaar_status = "UNAVAILABLE"
                findings.append((
                    "R02_APAAR_UNAVAILABLE_IN_ROSTER",
                    "LOW",
                    "APAAR identifier not provided in admission roster",
                    "Student record was submitted without a synthetic APAAR ID. Requires administrative follow-up to obtain synthetic identity identifier. Note: Missing APAAR status alone is an operational data gap, not proof of fraud."
                ))
            elif apaar.endswith("3"):
                apaar_status = "PENDING_VERIFICATION"
                findings.append((
                    "R02_APAAR_PENDING_ACKNOWLEDGEMENT",
                    "LOW",
                    "APAAR ID verification handshake pending acknowledgment",
                    f"Simulated verification adapter returned PENDING status for '{apaar}'. Note: Pending sync is an operational transition state, not proof of fraud or discrepancy."
                ))
            elif apaar.endswith("9"):
                apaar_status = "MISMATCH"
                findings.append((
                    "R02_APAAR_NAME_DISCREPANCY",
                    "MEDIUM",
                    "Identity name variation flagged between roster and simulated registry",
                    f"Simulated registry returns phonetic spelling variation for '{name}' with APAAR '{apaar}'. Reviewer triage required."
                ))
            else:
                apaar_status = "VERIFIED"

            # 2. Check for intra-batch duplicate enrolment number
            is_intra_batch_dup = False
            effective_enr = enr
            if not effective_enr:
                effective_enr = f"ENR-{uuid.uuid4().hex[:6].upper()}"
            elif effective_enr in seen_enrolments_in_batch:
                # Intra-batch duplicate: differentiate enrolment key and flag as duplicate
                is_intra_batch_dup = True
                effective_enr = f"{effective_enr}-DUP{records_processed}"
                findings.append((
                    "R03_DUPLICATE_CONCURRENT_ENROLMENT",
                    "HIGH",
                    f"Duplicate enrolment identifier '{enr}' detected in batch",
                    f"Enrolment number '{enr}' appeared multiple times within the same CSV intake batch '{batch_ref}'. Flagged for deduplication review."
                ))
            else:
                seen_enrolments_in_batch.add(effective_enr)

            # 3. Check for duplicate or concurrent APAAR identifier
            if apaar:
                if apaar in seen_apaars_in_batch:
                    findings.append((
                        "R03_DUPLICATE_CONCURRENT_ENROLMENT",
                        "HIGH",
                        f"Duplicate synthetic APAAR identifier '{apaar}' detected in batch",
                        f"Synthetic APAAR ID '{apaar}' was submitted multiple times within intake batch '{batch_ref}' under different enrolment records. Dual full-time technical enrolment is restricted under UGC Guidelines (April 2022)."
                    ))
                else:
                    # Check database for concurrent enrolment under a different enrolment number
                    concurrent_res = await db.execute(
                        select(StudentEnrolment).where(
                            StudentEnrolment.apaar_id == apaar,
                            StudentEnrolment.enrolment_number != effective_enr
                        )
                    )
                    concurrent_st = concurrent_res.scalars().first()
                    if concurrent_st:
                        findings.append((
                            "R03_DUPLICATE_CONCURRENT_ENROLMENT",
                            "HIGH",
                            f"Concurrent enrolment detected for APAAR identifier '{apaar}'",
                            f"Synthetic APAAR ID '{apaar}' is already enrolled in another student record ('{concurrent_st.student_name}', {concurrent_st.enrolment_number}) in the database. Dual full-time technical enrolment requires verification under UGC Guidelines (April 2022)."
                        ))
                    else:
                        seen_apaars_in_batch.add(apaar)

            # 4. Check if student with this enrolment_number already exists in database
            existing_student = None
            if effective_enr:
                existing_res = await db.execute(
                    select(StudentEnrolment).where(StudentEnrolment.enrolment_number == effective_enr)
                )
                existing_student = existing_res.scalar_one_or_none()

            # 5. Check approved intake capacity limit (R01_SANCTIONED_INTAKE_EXCEEDED)
            if not existing_student and matched_prog:
                curr_prog_id = matched_prog.id
                prog_enrolment_counts[curr_prog_id] = prog_enrolment_counts.get(curr_prog_id, 0) + 1
                curr_prog_count = prog_enrolment_counts[curr_prog_id]
                if matched_prog.sanctioned_intake and curr_prog_count > matched_prog.sanctioned_intake:
                    findings.append((
                        "R01_SANCTIONED_INTAKE_EXCEEDED",
                        "HIGH",
                        f"Enrolment exceeds sanctioned intake limit of {matched_prog.sanctioned_intake} seats ({matched_prog.academic_year}) [DEMO CONFIGURATION]",
                        f"Enrolment sequence #{curr_prog_count} exceeds approved capacity of {matched_prog.sanctioned_intake} seats for '{matched_prog.programme_name}' ({matched_prog.academic_year}). Sourced from institutional programme approval [DEMO CONFIGURATION]. Triage required to verify supernumerary or quota allocation."
                    ))

            display_name = name if name.endswith("[DEMO]") else f"{name} [DEMO]"
            if existing_student:
                # Version existing student record instead of crashing with Unique Constraint
                existing_student.version = (existing_student.version or 1) + 1
                existing_student.student_name = display_name
                existing_student.dob = row.get("dob") or existing_student.dob
                existing_student.gender = row.get("gender") or existing_student.gender
                existing_student.category = row.get("category") or existing_student.category
                existing_student.quota = row.get("quota") or existing_student.quota
                existing_student.admission_date = row.get("admission_date") or existing_student.admission_date
                existing_student.apaar_id = apaar or existing_student.apaar_id
                existing_student.apaar_status = apaar_status
                existing_student.updated_at = now

                # Query existing signals for this student to perform stable signal deduplication
                sig_stmt = select(IntegritySignal).where(IntegritySignal.student_id == existing_student.id)
                sig_res = await db.execute(sig_stmt)
                existing_signals = sig_res.scalars().all()

                active_signals = [s for s in existing_signals if s.review_status == "PENDING"]
                resolved_signals = [s for s in existing_signals if s.review_status != "PENDING"]

                # Process all findings with deduplication
                for f_rule, f_sev, f_sum, f_exp in findings:
                    has_active = any(s.rule_code == f_rule for s in active_signals)
                    has_resolved = any(s.rule_code == f_rule for s in resolved_signals)

                    if not has_active and not has_resolved:
                        sig = IntegritySignal(
                            id=str(uuid.uuid4()),
                            student_id=existing_student.id,
                            rule_code=f_rule,
                            severity=f_sev,
                            finding_summary=f_sum,
                            explanation=f_exp,
                            review_status="PENDING",
                            created_at=now,
                        )
                        db.add(sig)
                        active_signals.append(sig)

                # Clean/verified in current upload. Auto-resolve any pending APAAR flags if now verified.
                if apaar_status == "VERIFIED":
                    for s in active_signals:
                        if s.rule_code in ("R02_APAAR_PENDING_ACKNOWLEDGEMENT", "R02_APAAR_UNAVAILABLE_IN_ROSTER", "R02_APAAR_NAME_DISCREPANCY"):
                            s.review_status = "RESOLVED_VERIFIED"
                            s.reviewer_decision = "AUTO_RESOLVED_BY_INSPECTION"
                            s.reviewer_notes = "Automatically resolved: Student APAAR verification handshake completed successfully in subsequent intake roster."
                            s.reviewed_at = now

                remaining_active = [s for s in active_signals if s.review_status == "PENDING"]
                if remaining_active:
                    existing_student.integrity_status = "FLAGGED_FOR_REVIEW"
                    flagged_count += 1
                elif resolved_signals:
                    existing_student.integrity_status = "RESOLVED"
                    valid_count += 1
                else:
                    existing_student.integrity_status = "CLEARED"
                    valid_count += 1
            else:
                # Create new student enrolment
                student = StudentEnrolment(
                    id=str(uuid.uuid4()),
                    institution_id=inst.id,
                    programme_id=matched_prog.id if matched_prog else inst.id,
                    student_name=display_name,
                    apaar_id=apaar,
                    apaar_status=apaar_status,
                    dob=row.get("dob") or "2007-01-01",
                    gender=row.get("gender") or "Female",
                    category=row.get("category") or "General",
                    quota=row.get("quota") or "State Merit Quota",
                    enrolment_number=effective_enr,
                    admission_date=row.get("admission_date") or now.strftime("%Y-%m-%d"),
                    integrity_status="FLAGGED_FOR_REVIEW" if findings else "CLEARED",
                    version=1,
                    is_latest=True,
                    created_at=now,
                    updated_at=now,
                )
                db.add(student)
                await db.flush()

                if findings:
                    for f_rule, f_sev, f_sum, f_exp in findings:
                        sig = IntegritySignal(
                            id=str(uuid.uuid4()),
                            student_id=student.id,
                            rule_code=f_rule,
                            severity=f_sev,
                            finding_summary=f_sum,
                            explanation=f_exp,
                            review_status="PENDING",
                            created_at=now,
                        )
                        db.add(sig)
                    flagged_count += 1
                else:
                    valid_count += 1

        batch.total_records = records_processed
        batch.valid_records = valid_count
        batch.flagged_records = flagged_count
        batch.status = "REVIEW_REQUIRED" if flagged_count > 0 else "COMPLETED"

        # Add audit log entry
        thash = generate_tamper_hash(
            "institution_admin@apex.edu",
            "BATCH_CSV_UPLOAD",
            f"intake_batches/{batch_ref}",
            now.isoformat()
        )
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
    except Exception as exc:
        await db.rollback()
        logger.error(f"Failed intake CSV upload transaction: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Database transaction failure during intake processing: {str(exc)}",
        )

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
        "message": f"Successfully processed intake batch {batch_ref} with {records_processed} synthetic student records ({valid_count} verified, {flagged_count} flagged for review).",
    }
