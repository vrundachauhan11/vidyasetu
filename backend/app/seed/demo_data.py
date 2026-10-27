"""Realistic synthetic demo data seeder for VidyaSetu.
All data in this file is strictly SYNTHETIC and generated for demonstration purposes.
Never uses real student records, real Aadhaar, or live APAAR numbers.
Provides a completely safe, idempotent seeding routine compatible with PostgreSQL and SQLite.
"""
import hashlib
import json
import uuid
from typing import Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    Institution,
    ProgrammeApproval,
    StudentEnrolment,
    IntakeBatch,
    IntegritySignal,
    AuditLog,
    utc_now,
)
from app.logging_config import logger


def generate_tamper_hash(actor: str, action: str, resource: str, timestamp_str: str) -> str:
    content = f"{actor}|{action}|{resource}|{timestamp_str}|vidyasetu-demo-salt"
    return hashlib.sha256(content.encode()).hexdigest()


async def seed_demo_data_if_empty(session: AsyncSession) -> Dict[str, Any]:
    """Safely and idempotently populate database with canonical synthetic institutional demo data.
    Never overwrites existing records, existing reviewer decisions, or user modifications.
    """
    logger.info("Verifying and synchronizing canonical demo dataset...")
    now = utc_now()

    # 1. Institutions
    institutions_spec = [
        {
            "aicte_id": "DEMO-AICTE-1-0091823",
            "name": "Apex Institute of Technology & Management [DEMO]",
            "state": "Delhi",
            "district": "South West Delhi",
            "institution_type": "Engineering & Technology",
            "approval_status": "Approved (EOA 2025-26)",
        },
        {
            "aicte_id": "DEMO-AICTE-1-0045192",
            "name": "Kalinga Academy of Engineering [DEMO]",
            "state": "Odisha",
            "district": "Khurda",
            "institution_type": "Engineering & Technology",
            "approval_status": "Approved (EOA 2025-26)",
        },
        {
            "aicte_id": "DEMO-AICTE-1-0082736",
            "name": "Sahyadri Polytechnic & Engineering College [DEMO]",
            "state": "Maharashtra",
            "district": "Pune",
            "institution_type": "Engineering & Technology",
            "approval_status": "Approved (EOA 2025-26)",
        },
    ]

    inst_map = {}
    for spec in institutions_spec:
        stmt = select(Institution).where(Institution.aicte_id == spec["aicte_id"])
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            inst = Institution(
                id=str(uuid.uuid4()),
                aicte_id=spec["aicte_id"],
                name=spec["name"],
                state=spec["state"],
                district=spec["district"],
                institution_type=spec["institution_type"],
                approval_status=spec["approval_status"],
                created_at=now,
            )
            session.add(inst)
            await session.flush()
            inst_map[spec["aicte_id"]] = inst
        else:
            inst_map[spec["aicte_id"]] = existing

    # 2. Programme Approvals with Sanctioned Intakes
    inst1 = inst_map["DEMO-AICTE-1-0091823"]
    inst2 = inst_map["DEMO-AICTE-1-0045192"]

    programmes_spec = [
        {
            "key": "CSE_APEX",
            "inst_id": inst1.id,
            "programme_name": "B.Tech Computer Science and Engineering",
            "degree_level": "Undergraduate",
            "academic_year": "2025-26",
            "sanctioned_intake": 120,
            "approved_quota_details": "State Quota 85% (102), Management Quota 15% (18)",
        },
        {
            "key": "ECE_APEX",
            "inst_id": inst1.id,
            "programme_name": "B.Tech Electronics & Communication Engineering",
            "degree_level": "Undergraduate",
            "academic_year": "2025-26",
            "sanctioned_intake": 60,
            "approved_quota_details": "State Quota 85% (51), Management Quota 15% (9)",
        },
        {
            "key": "IT_KALINGA",
            "inst_id": inst2.id,
            "programme_name": "B.Tech Information Technology",
            "degree_level": "Undergraduate",
            "academic_year": "2025-26",
            "sanctioned_intake": 60,
            "approved_quota_details": "State Merit 85% (51), All India Quota 15% (9)",
        },
        {
            "key": "AIDS_APEX",
            "inst_id": inst1.id,
            "programme_name": "B.Tech Artificial Intelligence & Data Science",
            "degree_level": "Undergraduate",
            "academic_year": "2025-26",
            "sanctioned_intake": 60,
            "approved_quota_details": "State Quota 100% (60 seats)",
        },
    ]

    prog_map = {}
    for ps in programmes_spec:
        stmt = select(ProgrammeApproval).where(
            ProgrammeApproval.institution_id == ps["inst_id"],
            ProgrammeApproval.programme_name == ps["programme_name"],
            ProgrammeApproval.academic_year == ps["academic_year"],
        )
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            prog = ProgrammeApproval(
                id=str(uuid.uuid4()),
                institution_id=ps["inst_id"],
                programme_name=ps["programme_name"],
                degree_level=ps["degree_level"],
                academic_year=ps["academic_year"],
                sanctioned_intake=ps["sanctioned_intake"],
                approved_quota_details=ps["approved_quota_details"],
                created_at=now,
            )
            session.add(prog)
            await session.flush()
            prog_map[ps["key"]] = prog
        else:
            prog_map[ps["key"]] = existing

    # 3. Intake Batches
    batches_spec = [
        {
            "inst_id": inst1.id,
            "batch_reference": "DEMO-BATCH-2025-08-01",
            "academic_year": "2025-26",
            "filename": "Apex_CSE_Admissions_Round1_Synthetic.csv",
            "total_records": 122,
            "valid_records": 119,
            "flagged_records": 3,
            "status": "REVIEW_REQUIRED",
        },
        {
            "inst_id": inst2.id,
            "batch_reference": "DEMO-BATCH-2025-08-02",
            "academic_year": "2025-26",
            "filename": "Kalinga_IT_Admissions_Round1_Synthetic.csv",
            "total_records": 58,
            "valid_records": 58,
            "flagged_records": 0,
            "status": "COMPLETED",
        },
    ]

    for bs in batches_spec:
        stmt = select(IntakeBatch).where(IntakeBatch.batch_reference == bs["batch_reference"])
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            batch = IntakeBatch(
                id=str(uuid.uuid4()),
                institution_id=bs["inst_id"],
                batch_reference=bs["batch_reference"],
                academic_year=bs["academic_year"],
                filename=bs["filename"],
                total_records=bs["total_records"],
                valid_records=bs["valid_records"],
                flagged_records=bs["flagged_records"],
                status=bs["status"],
                uploaded_at=now,
            )
            session.add(batch)
            await session.flush()

    # 4. Synthetic Student Enrolments (13 Canonical Scenario Records)
    cse_prog = prog_map["CSE_APEX"]
    ece_prog = prog_map["ECE_APEX"]

    students_spec = [
        {"key": "s1", "name": "Ananya Sharma [DEMO]", "apaar_id": "DEMO-APAAR-2026-904128", "apaar_status": "VERIFIED", "dob": "2007-04-12", "gender": "Female", "category": "General", "quota": "State Merit Quota", "enrolment_number": "ENR-2025-CSE-001", "integrity_status": "CLEARED", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s2", "name": "Rohan Patel [DEMO]", "apaar_id": "DEMO-APAAR-2026-904129", "apaar_status": "VERIFIED", "dob": "2006-11-20", "gender": "Male", "category": "OBC-NCL", "quota": "State Merit Quota", "enrolment_number": "ENR-2025-CSE-002", "integrity_status": "CLEARED", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s3", "name": "Pooja V. Nair [DEMO]", "apaar_id": "DEMO-APAAR-2026-904130", "apaar_status": "PENDING_VERIFICATION", "dob": "2007-02-15", "gender": "Female", "category": "General", "quota": "State Merit Quota", "enrolment_number": "ENR-2025-CSE-003", "integrity_status": "FLAGGED_FOR_REVIEW", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s4", "name": "Aarav S. Verma [DEMO]", "apaar_id": "DEMO-APAAR-2026-904131", "apaar_status": "MISMATCH", "dob": "2006-08-30", "gender": "Male", "category": "EWS", "quota": "Institutional / Management", "enrolment_number": "ENR-2025-CSE-004", "integrity_status": "FLAGGED_FOR_REVIEW", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s5", "name": "Kavya Krishnan [DEMO]", "apaar_id": "DEMO-APAAR-2026-904140", "apaar_status": "VERIFIED", "dob": "2007-03-10", "gender": "Female", "category": "General", "quota": "State Merit Quota", "enrolment_number": "ENR-2025-CSE-005", "integrity_status": "CLEARED", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s6", "name": "Devansh Singhania [DEMO]", "apaar_id": "DEMO-APAAR-2026-904141", "apaar_status": "VERIFIED", "dob": "2006-12-04", "gender": "Male", "category": "General", "quota": "Management Quota", "enrolment_number": "ENR-2025-CSE-006", "integrity_status": "CLEARED", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s7", "name": "Meera Joshi [DEMO]", "apaar_id": "DEMO-APAAR-2026-904142", "apaar_status": "VERIFIED", "dob": "2007-07-22", "gender": "Female", "category": "OBC-NCL", "quota": "State Merit Quota", "enrolment_number": "ENR-2025-CSE-007", "integrity_status": "CLEARED", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s8", "name": "Tarun Balakrishnan [DEMO]", "apaar_id": "DEMO-APAAR-2026-904143", "apaar_status": "PENDING_VERIFICATION", "dob": "2006-05-18", "gender": "Male", "category": "SC", "quota": "State Merit Quota", "enrolment_number": "ENR-2025-CSE-008", "integrity_status": "RESOLVED", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s9", "name": "Simran Kaur [DEMO]", "apaar_id": "DEMO-APAAR-2026-904144", "apaar_status": "VERIFIED", "dob": "2007-09-01", "gender": "Female", "category": "EWS", "quota": "State Merit Quota", "enrolment_number": "ENR-2025-CSE-009", "integrity_status": "CLEARED", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s10", "name": "Siddharth Rao [DEMO]", "apaar_id": "DEMO-APAAR-2026-904132", "apaar_status": "VERIFIED", "dob": "2007-06-05", "gender": "Male", "category": "General", "quota": "Management Quota", "enrolment_number": "ENR-2025-CSE-121", "integrity_status": "FLAGGED_FOR_REVIEW", "prog_id": cse_prog.id, "inst_id": inst1.id},
        {"key": "s11", "name": "Farida Begum [DEMO]", "apaar_id": "", "apaar_status": "UNAVAILABLE", "dob": "2007-05-18", "gender": "Female", "category": "General", "quota": "Management Quota", "enrolment_number": "REG-UNAV-74C474-03", "integrity_status": "FLAGGED_FOR_REVIEW", "prog_id": ece_prog.id, "inst_id": inst1.id},
        {"key": "s12", "name": "Gaurav Sen [DEMO]", "apaar_id": "DEMO-APAAR-2026-DP174C0", "apaar_status": "VERIFIED", "dob": "2007-01-10", "gender": "Male", "category": "General", "quota": "State Merit Quota", "enrolment_number": "REG-DUP-74C474-05", "integrity_status": "CLEARED", "prog_id": ece_prog.id, "inst_id": inst1.id},
        {"key": "s13", "name": "Gaurav Sen (Duplicate Entry) [DEMO]", "apaar_id": "DEMO-APAAR-2026-DP274C0", "apaar_status": "VERIFIED", "dob": "2007-01-10", "gender": "Male", "category": "General", "quota": "State Merit Quota", "enrolment_number": "REG-DUP-74C474-05-DUP6", "integrity_status": "FLAGGED_FOR_REVIEW", "prog_id": ece_prog.id, "inst_id": inst1.id},
    ]

    student_map = {}
    for s_dict in students_spec:
        stmt = select(StudentEnrolment).where(StudentEnrolment.enrolment_number == s_dict["enrolment_number"])
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            student = StudentEnrolment(
                id=str(uuid.uuid4()),
                institution_id=s_dict["inst_id"],
                programme_id=s_dict["prog_id"],
                student_name=s_dict["name"],
                apaar_id=s_dict["apaar_id"],
                apaar_status=s_dict["apaar_status"],
                dob=s_dict["dob"],
                gender=s_dict["gender"],
                category=s_dict["category"],
                quota=s_dict["quota"],
                enrolment_number=s_dict["enrolment_number"],
                integrity_status=s_dict["integrity_status"],
                version=1,
                is_latest=True,
                created_at=now,
            )
            session.add(student)
            await session.flush()
            student_map[s_dict["key"]] = student
        else:
            student_map[s_dict["key"]] = existing

    # 5. Integrity Signals with Explainable Deterministic Findings
    signals_spec = [
        # Signal 1: Pending APAAR verification (Pooja V. Nair)
        {
            "student_key": "s3",
            "rule_code": "R02_APAAR_PENDING_ACKNOWLEDGEMENT",
            "severity": "LOW",
            "finding_summary": "APAAR ID Verification Pending (Institutional Sync in Progress)",
            "explanation": "Synthetic APAAR reference DEMO-APAAR-2026-904130 was submitted but has not yet returned an automated verification handshake from DigiLocker/APAAR Mock. Notice: Missing or pending APAAR status is an operational signal and does NOT imply fraud.",
            "review_status": "PENDING",
            "reviewer_decision": None,
            "reviewer_notes": None,
            "reviewed_at": None,
        },
        # Signal 2: APAAR Name Discrepancy (Aarav S. Verma)
        {
            "student_key": "s4",
            "rule_code": "R02_APAAR_NAME_DISCREPANCY",
            "severity": "MEDIUM",
            "finding_summary": "Slight mismatch in spelling between Institute Enrolment and APAAR Record",
            "explanation": "Institutional roster records 'Aarav S. Verma', whereas simulated APAAR registry returns 'Arav Verma'. Phonetic match score: 88%. Requires reviewer verification against Class 10/12 certificate.",
            "review_status": "PENDING",
            "reviewer_decision": None,
            "reviewer_notes": None,
            "reviewed_at": None,
        },
        # Signal 3: Sanctioned Intake Overrun (Siddharth Rao)
        {
            "student_key": "s10",
            "rule_code": "R01_SANCTIONED_INTAKE_EXCEEDED",
            "severity": "HIGH",
            "finding_summary": "Enrolment exceeds AICTE approved intake capacity of 120 seats",
            "explanation": "Enrolment sequence #121 exceeds the sanctioned intake limit of 120 seats for B.Tech CSE (Academic Year 2025-26). Institutional review required to determine if student qualifies under Supernumerary / PMSSS / EWS quota or if seat reallocation is needed.",
            "review_status": "PENDING",
            "reviewer_decision": None,
            "reviewer_notes": None,
            "reviewed_at": None,
        },
        # Signal 4: Tarun Balakrishnan Resolved Signal 1
        {
            "student_key": "s8",
            "rule_code": "R02_APAAR_MOCK_DISCREPANCY",
            "severity": "MEDIUM",
            "finding_summary": "Mock identity discrepancy resolved against verified council roster",
            "explanation": "Reviewer confirmed admission ledger and identity proof matches institutional physical records.",
            "review_status": "RESOLVED_ACCEPTED",
            "reviewer_decision": "RESOLVED_ACCEPTED",
            "reviewer_notes": "Runtime verification test decision: verified against council roster",
            "reviewed_at": now,
        },
        # Signal 5: Tarun Balakrishnan Resolved Signal 2
        {
            "student_key": "s8",
            "rule_code": "R02_APAAR_PENDING_ACKNOWLEDGEMENT",
            "severity": "MEDIUM",
            "finding_summary": "APAAR verification delayed in mock adapter",
            "explanation": "Pending status acknowledged. No adverse conclusion drawn.",
            "review_status": "RESOLVED_ACCEPTED",
            "reviewer_decision": "RESOLVED_ACCEPTED",
            "reviewer_notes": "Synthetic demo review: APAAR status is pending in the simulated adapter. No adverse conclusion is drawn. Await acknowledgement and recheck status",
            "reviewed_at": now,
        },
        # Signal 6: Farida Begum Missing APAAR
        {
            "student_key": "s11",
            "rule_code": "R02_APAAR_UNAVAILABLE_IN_ROSTER",
            "severity": "LOW",
            "finding_summary": "APAAR ID Unavailable in Submitted Institutional Roster",
            "explanation": "No APAAR identifier provided in the intake batch. Mandatory DigiLocker onboarding required within 60 days.",
            "review_status": "PENDING",
            "reviewer_decision": None,
            "reviewer_notes": None,
            "reviewed_at": None,
        },
        # Signal 7: Gaurav Sen Concurrent Duplicate Enrolment
        {
            "student_key": "s13",
            "rule_code": "R03_DUPLICATE_CONCURRENT_ENROLMENT",
            "severity": "HIGH",
            "finding_summary": "Duplicate enrolment number detected within same institution roster",
            "explanation": "Enrolment number REG-DUP-74C474-05 was submitted for two distinct entries. Immediate verification required.",
            "review_status": "PENDING",
            "reviewer_decision": None,
            "reviewer_notes": None,
            "reviewed_at": None,
        },
    ]

    for sig_spec in signals_spec:
        st = student_map[sig_spec["student_key"]]
        stmt = select(IntegritySignal).where(
            IntegritySignal.student_id == st.id,
            IntegritySignal.rule_code == sig_spec["rule_code"],
        )
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if not existing:
            sig = IntegritySignal(
                id=str(uuid.uuid4()),
                student_id=st.id,
                rule_code=sig_spec["rule_code"],
                severity=sig_spec["severity"],
                finding_summary=sig_spec["finding_summary"],
                explanation=sig_spec["explanation"],
                review_status=sig_spec["review_status"],
                reviewer_decision=sig_spec["reviewer_decision"],
                reviewer_notes=sig_spec["reviewer_notes"],
                reviewed_at=sig_spec["reviewed_at"],
                created_at=now,
            )
            session.add(sig)
            await session.flush()

    # 6. Audit Logs
    audit_count = (await session.execute(select(func.count(AuditLog.id)))).scalar() or 0
    if audit_count == 0:
        audit_entries = [
            ("institution_admin@apex.edu", "INSTITUTION_ADMIN", "BATCH_CSV_UPLOAD", "intake_batches/DEMO-BATCH-2025-08-01", {"filename": "Apex_CSE_Admissions_Round1_Synthetic.csv", "records": 122}),
            ("system_rule_engine@vidyasetu.local", "SYSTEM", "APAAR_MOCK_VALIDATION", "apaar_adapter/DEMO-BATCH-2025-08-01", {"verified": 119, "pending": 1, "mismatched": 1}),
            ("system_rule_engine@vidyasetu.local", "SYSTEM", "INTEGRITY_RULES_EVALUATION", "rule_registry/Apex_CSE", {"rules_evaluated": 8, "signals_generated": 3}),
            ("compliance_officer@aicte-gov.in", "COMPLIANCE_REVIEWER", "FLAG_TRIAGE_OPENED", "integrity_signals/R01_SANCTIONED_INTAKE_EXCEEDED", {"status": "Review in progress"}),
            ("reviewer.desk@vidyasetu.local", "COMPLIANCE_REVIEWER", "SIGNAL_REVIEW_DECISION", "integrity_signals/Tarun_Mock_Discrepancy", {"decision": "RESOLVED_ACCEPTED", "notes": "Runtime verification test decision: verified against council roster"}),
            ("reviewer.desk@vidyasetu.local", "COMPLIANCE_REVIEWER", "SIGNAL_REVIEW_DECISION", "integrity_signals/Tarun_Pending_Ack", {"decision": "RESOLVED_ACCEPTED", "notes": "Synthetic demo review: APAAR status is pending in the simulated adapter. No adverse conclusion is drawn. Await acknowledgement and recheck status"}),
        ]
        for actor, role, action, resource, details in audit_entries:
            ts = now.isoformat()
            thash = generate_tamper_hash(actor, action, resource, ts)
            log = AuditLog(
                id=str(uuid.uuid4()),
                timestamp=now,
                actor=actor,
                role=role,
                action=action,
                resource=resource,
                details_json=json.dumps(details),
                tamper_hash=thash,
            )
            session.add(log)
        await session.flush()

    await session.commit()

    # Final counts for observability
    inst_c = (await session.execute(select(func.count(Institution.id)))).scalar() or 0
    prog_c = (await session.execute(select(func.count(ProgrammeApproval.id)))).scalar() or 0
    st_c = (await session.execute(select(func.count(StudentEnrolment.id)))).scalar() or 0
    sig_c = (await session.execute(select(func.count(IntegritySignal.id)))).scalar() or 0
    aud_c = (await session.execute(select(func.count(AuditLog.id)))).scalar() or 0

    stats = {
        "institutions": inst_c,
        "programmes": prog_c,
        "students": st_c,
        "signals": sig_c,
        "audit_logs": aud_c,
    }
    logger.info(f"Canonical demo data synchronized: {stats}")
    return stats
