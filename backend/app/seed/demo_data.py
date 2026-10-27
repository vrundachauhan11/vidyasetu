"""Realistic synthetic demo data seeder for VidyaSetu.
All data in this file is strictly SYNTHETIC and generated for demonstration purposes.
Never uses real student records, real Aadhaar, or live APAAR numbers.
"""
import hashlib
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (
    Institution,
    ProgrammeApproval,
    StudentEnrolment,
    IntakeBatch,
    IntegritySignal,
    AuditLog,
)
from app.logging_config import logger


def generate_tamper_hash(actor: str, action: str, resource: str, timestamp_str: str) -> str:
    content = f"{actor}|{action}|{resource}|{timestamp_str}|vidyasetu-demo-salt"
    return hashlib.sha256(content.encode()).hexdigest()


async def seed_demo_data_if_empty(session: AsyncSession) -> bool:
    """Populate database with synthetic institutional demo data if empty."""
    res = await session.execute(select(func.count(Institution.id)))
    count = res.scalar() or 0
    if count > 0:
        logger.info("Demo data already seeded; skipping initial seed.")
        return False

    logger.info("Seeding realistic synthetic demo data into VidyaSetu...")

    now = datetime.now(timezone.utc)

    # 1. Institutions
    inst1 = Institution(
        id=str(uuid.uuid4()),
        aicte_id="DEMO-AICTE-1-0091823",
        name="Apex Institute of Technology & Management [DEMO]",
        state="Delhi",
        district="South West Delhi",
        institution_type="Engineering & Technology",
        approval_status="Approved (EOA 2025-26)",
        created_at=now,
    )
    inst2 = Institution(
        id=str(uuid.uuid4()),
        aicte_id="DEMO-AICTE-1-0045192",
        name="Kalinga Academy of Engineering [DEMO]",
        state="Odisha",
        district="Khurda",
        institution_type="Engineering & Technology",
        approval_status="Approved (EOA 2025-26)",
        created_at=now,
    )
    inst3 = Institution(
        id=str(uuid.uuid4()),
        aicte_id="DEMO-AICTE-1-0082736",
        name="Sahyadri Polytechnic & Engineering College [DEMO]",
        state="Maharashtra",
        district="Pune",
        institution_type="Engineering & Technology",
        approval_status="Approved (EOA 2025-26)",
        created_at=now,
    )
    session.add_all([inst1, inst2, inst3])
    await session.flush()

    # 2. Programme Approvals with Sanctioned Intakes
    prog1 = ProgrammeApproval(
        id=str(uuid.uuid4()),
        institution_id=inst1.id,
        programme_name="B.Tech Computer Science and Engineering",
        degree_level="Undergraduate",
        academic_year="2025-26",
        sanctioned_intake=120,
        approved_quota_details="State Quota 85% (102), Management Quota 15% (18)",
        created_at=now,
    )
    prog2 = ProgrammeApproval(
        id=str(uuid.uuid4()),
        institution_id=inst1.id,
        programme_name="B.Tech Electronics & Communication Engineering",
        degree_level="Undergraduate",
        academic_year="2025-26",
        sanctioned_intake=60,
        approved_quota_details="State Quota 85% (51), Management Quota 15% (9)",
        created_at=now,
    )
    prog3 = ProgrammeApproval(
        id=str(uuid.uuid4()),
        institution_id=inst2.id,
        programme_name="B.Tech Information Technology",
        degree_level="Undergraduate",
        academic_year="2025-26",
        sanctioned_intake=60,
        approved_quota_details="State Merit 85% (51), All India Quota 15% (9)",
        created_at=now,
    )
    prog4 = ProgrammeApproval(
        id=str(uuid.uuid4()),
        institution_id=inst1.id,
        programme_name="B.Tech Artificial Intelligence & Data Science",
        degree_level="Undergraduate",
        academic_year="2025-26",
        sanctioned_intake=60,
        approved_quota_details="State Quota 100% (60 seats)",
        created_at=now,
    )
    session.add_all([prog1, prog2, prog3, prog4])
    await session.flush()

    # 3. Intake Batches
    batch1 = IntakeBatch(
        id=str(uuid.uuid4()),
        institution_id=inst1.id,
        batch_reference="DEMO-BATCH-2025-08-01",
        academic_year="2025-26",
        filename="Apex_CSE_Admissions_Round1_Synthetic.csv",
        total_records=122,
        valid_records=119,
        flagged_records=3,
        status="REVIEW_REQUIRED",
        uploaded_at=now,
    )
    batch2 = IntakeBatch(
        id=str(uuid.uuid4()),
        institution_id=inst2.id,
        batch_reference="DEMO-BATCH-2025-08-02",
        academic_year="2025-26",
        filename="Kalinga_IT_Admissions_Round1_Synthetic.csv",
        total_records=58,
        valid_records=58,
        flagged_records=0,
        status="COMPLETED",
        uploaded_at=now,
    )
    session.add_all([batch1, batch2])
    await session.flush()

    # 4. Synthetic Student Enrolments
    students_data = [
        # 1. Normal verified student
        {
            "name": "Ananya Sharma [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904128",
            "apaar_status": "VERIFIED",
            "dob": "2007-04-12",
            "gender": "Female",
            "category": "General",
            "quota": "State Merit Quota",
            "enrolment_number": "ENR-2025-CSE-001",
            "integrity_status": "CLEARED",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 2. Normal verified student
        {
            "name": "Rohan Patel [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904129",
            "apaar_status": "VERIFIED",
            "dob": "2006-11-20",
            "gender": "Male",
            "category": "OBC-NCL",
            "quota": "State Merit Quota",
            "enrolment_number": "ENR-2025-CSE-002",
            "integrity_status": "CLEARED",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 3. Pending APAAR student (normal operational verification delay, NOT fraud)
        {
            "name": "Pooja V. Nair [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904130",
            "apaar_status": "PENDING_VERIFICATION",
            "dob": "2007-02-15",
            "gender": "Female",
            "category": "General",
            "quota": "State Merit Quota",
            "enrolment_number": "ENR-2025-CSE-003",
            "integrity_status": "FLAGGED_FOR_REVIEW",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 4. Student with APAAR Identity Mismatch (Name spelling discrepancy)
        {
            "name": "Aarav S. Verma [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904131",
            "apaar_status": "MISMATCH",
            "dob": "2006-08-30",
            "gender": "Male",
            "category": "EWS",
            "quota": "Institutional / Management",
            "enrolment_number": "ENR-2025-CSE-004",
            "integrity_status": "FLAGGED_FOR_REVIEW",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 5. Verified batch intake student
        {
            "name": "Kavya Krishnan [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904140",
            "apaar_status": "VERIFIED",
            "dob": "2007-03-10",
            "gender": "Female",
            "category": "General",
            "quota": "State Merit Quota",
            "enrolment_number": "ENR-2025-CSE-005",
            "integrity_status": "CLEARED",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 6. Verified batch intake student
        {
            "name": "Devansh Singhania [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904141",
            "apaar_status": "VERIFIED",
            "dob": "2006-12-04",
            "gender": "Male",
            "category": "General",
            "quota": "Management Quota",
            "enrolment_number": "ENR-2025-CSE-006",
            "integrity_status": "CLEARED",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 7. Verified batch intake student
        {
            "name": "Meera Joshi [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904142",
            "apaar_status": "VERIFIED",
            "dob": "2007-07-22",
            "gender": "Female",
            "category": "OBC-NCL",
            "quota": "State Merit Quota",
            "enrolment_number": "ENR-2025-CSE-007",
            "integrity_status": "CLEARED",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 8. Student with Resolved Reviewer Decision
        {
            "name": "Tarun Balakrishnan [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904143",
            "apaar_status": "PENDING_VERIFICATION",
            "dob": "2006-05-18",
            "gender": "Male",
            "category": "SC",
            "quota": "State Merit Quota",
            "enrolment_number": "ENR-2025-CSE-008",
            "integrity_status": "RESOLVED",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 9. Verified batch intake student
        {
            "name": "Simran Kaur [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904144",
            "apaar_status": "VERIFIED",
            "dob": "2007-09-01",
            "gender": "Female",
            "category": "EWS",
            "quota": "State Merit Quota",
            "enrolment_number": "ENR-2025-CSE-009",
            "integrity_status": "CLEARED",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 10. Student over sanctioned intake limit
        {
            "name": "Siddharth Rao [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-904132",
            "apaar_status": "VERIFIED",
            "dob": "2007-06-05",
            "gender": "Male",
            "category": "General",
            "quota": "Management Quota",
            "enrolment_number": "ENR-2025-CSE-121",
            "integrity_status": "FLAGGED_FOR_REVIEW",
            "prog_id": prog1.id,
            "inst_id": inst1.id,
        },
        # 11. Missing APAAR in Roster
        {
            "name": "Farida Begum [DEMO]",
            "apaar_id": "",
            "apaar_status": "UNAVAILABLE",
            "dob": "2007-05-18",
            "gender": "Female",
            "category": "General",
            "quota": "Management Quota",
            "enrolment_number": "REG-UNAV-74C474-03",
            "integrity_status": "FLAGGED_FOR_REVIEW",
            "prog_id": prog2.id,
            "inst_id": inst1.id,
        },
        # 12. Duplicate Enrolment Pair - Record 1 (Cleared entry)
        {
            "name": "Gaurav Sen [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-DP174C0",
            "apaar_status": "VERIFIED",
            "dob": "2007-01-10",
            "gender": "Male",
            "category": "General",
            "quota": "State Merit Quota",
            "enrolment_number": "REG-DUP-74C474-05",
            "integrity_status": "CLEARED",
            "prog_id": prog2.id,
            "inst_id": inst1.id,
        },
        # 13. Duplicate Enrolment Pair - Record 2 (Flagged concurrent entry)
        {
            "name": "Gaurav Sen (Duplicate Entry) [DEMO]",
            "apaar_id": "DEMO-APAAR-2026-DP274C0",
            "apaar_status": "VERIFIED",
            "dob": "2007-01-10",
            "gender": "Male",
            "category": "General",
            "quota": "State Merit Quota",
            "enrolment_number": "REG-DUP-74C474-05-DUP6",
            "integrity_status": "FLAGGED_FOR_REVIEW",
            "prog_id": prog2.id,
            "inst_id": inst1.id,
        },
    ]

    created_students = []
    for s_dict in students_data:
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
        created_students.append(student)

    await session.flush()

    # 5. Integrity Signals with Explainable Deterministic Findings
    # Signal 1: Pending APAAR verification (Pooja V. Nair, index 2)
    sig1 = IntegritySignal(
        id=str(uuid.uuid4()),
        student_id=created_students[2].id,
        rule_code="R02_APAAR_PENDING_ACKNOWLEDGEMENT",
        severity="LOW",
        finding_summary="APAAR ID Verification Pending (Institutional Sync in Progress)",
        explanation="Synthetic APAAR reference DEMO-APAAR-2026-904130 was submitted but has not yet returned an automated verification handshake from DigiLocker/APAAR Mock. Notice: Missing or pending APAAR status is an operational signal and does NOT imply fraud.",
        review_status="PENDING",
        created_at=now,
    )
    # Signal 2: APAAR Name Discrepancy (Aarav S. Verma, index 3)
    sig2 = IntegritySignal(
        id=str(uuid.uuid4()),
        student_id=created_students[3].id,
        rule_code="R02_APAAR_NAME_DISCREPANCY",
        severity="MEDIUM",
        finding_summary="Slight mismatch in spelling between Institute Enrolment and APAAR Record",
        explanation="Institutional roster records 'Aarav S. Verma', whereas simulated APAAR registry returns 'Arav Verma'. Phonetic match score: 88%. Requires reviewer verification against Class 10/12 certificate.",
        review_status="PENDING",
        created_at=now,
    )
    # Signal 3: Sanctioned Intake Overrun (Siddharth Rao, index 9)
    sig3 = IntegritySignal(
        id=str(uuid.uuid4()),
        student_id=created_students[9].id,
        rule_code="R01_SANCTIONED_INTAKE_EXCEEDED",
        severity="HIGH",
        finding_summary="Enrolment exceeds AICTE approved intake capacity of 120 seats",
        explanation="Enrolment sequence #121 exceeds the sanctioned intake limit of 120 seats for B.Tech CSE (Academic Year 2025-26). Institutional review required to determine if student qualifies under Supernumerary / PMSSS / EWS quota or if seat reallocation is needed.",
        review_status="PENDING",
        created_at=now,
    )
    # Signal 4: Tarun Balakrishnan Resolved Signal 1 (index 7)
    sig4 = IntegritySignal(
        id=str(uuid.uuid4()),
        student_id=created_students[7].id,
        rule_code="R02_APAAR_MOCK_DISCREPANCY",
        severity="MEDIUM",
        finding_summary="Mock identity discrepancy resolved against verified council roster",
        explanation="Reviewer confirmed admission ledger and identity proof matches institutional physical records.",
        review_status="RESOLVED_ACCEPTED",
        reviewer_decision="RESOLVED_ACCEPTED",
        reviewer_notes="Runtime verification test decision: verified against council roster",
        reviewed_at=now,
        created_at=now,
    )
    # Signal 5: Tarun Balakrishnan Resolved Signal 2 (index 7)
    sig5 = IntegritySignal(
        id=str(uuid.uuid4()),
        student_id=created_students[7].id,
        rule_code="R02_APAAR_PENDING_ACKNOWLEDGEMENT",
        severity="MEDIUM",
        finding_summary="APAAR verification delayed in mock adapter",
        explanation="Pending status acknowledged. No adverse conclusion drawn.",
        review_status="RESOLVED_ACCEPTED",
        reviewer_decision="RESOLVED_ACCEPTED",
        reviewer_notes="Synthetic demo review: APAAR status is pending in the simulated adapter. No adverse conclusion is drawn. Await acknowledgement and recheck status",
        reviewed_at=now,
        created_at=now,
    )
    # Signal 6: Farida Begum Missing APAAR (index 10)
    sig6 = IntegritySignal(
        id=str(uuid.uuid4()),
        student_id=created_students[10].id,
        rule_code="R02_APAAR_UNAVAILABLE_IN_ROSTER",
        severity="LOW",
        finding_summary="APAAR ID Unavailable in Submitted Institutional Roster",
        explanation="No APAAR identifier provided in the intake batch. Mandatory DigiLocker onboarding required within 60 days.",
        review_status="PENDING",
        created_at=now,
    )
    # Signal 7: Gaurav Sen Concurrent Duplicate Enrolment (index 12)
    sig7 = IntegritySignal(
        id=str(uuid.uuid4()),
        student_id=created_students[12].id,
        rule_code="R03_DUPLICATE_CONCURRENT_ENROLMENT",
        severity="HIGH",
        finding_summary="Duplicate enrolment number detected within same institution roster",
        explanation="Enrolment number REG-DUP-74C474-05 was submitted for two distinct entries. Immediate verification required.",
        review_status="PENDING",
        created_at=now,
    )
    session.add_all([sig1, sig2, sig3, sig4, sig5, sig6, sig7])
    await session.flush()

    # 6. Audit Logs
    audit_entries = [
        ("institution_admin@apex.edu", "INSTITUTION_ADMIN", "BATCH_CSV_UPLOAD", "intake_batches/DEMO-BATCH-2025-08-01", {"filename": "Apex_CSE_Admissions_Round1_Synthetic.csv", "records": 122}),
        ("system_rule_engine@vidyasetu.local", "SYSTEM", "APAAR_MOCK_VALIDATION", "apaar_adapter/DEMO-BATCH-2025-08-01", {"verified": 119, "pending": 1, "mismatched": 1}),
        ("system_rule_engine@vidyasetu.local", "SYSTEM", "INTEGRITY_RULES_EVALUATION", "rule_registry/Apex_CSE", {"rules_evaluated": 8, "signals_generated": 3}),
        ("compliance_officer@aicte-gov.in", "COMPLIANCE_REVIEWER", "FLAG_TRIAGE_OPENED", "integrity_signals/R01_SANCTIONED_INTAKE_EXCEEDED", {"status": "Review in progress"}),
        ("reviewer.desk@vidyasetu.local", "COMPLIANCE_REVIEWER", "SIGNAL_REVIEW_DECISION", f"integrity_signals/{sig4.id}", {"decision": "RESOLVED_ACCEPTED", "notes": "Runtime verification test decision: verified against council roster"}),
        ("reviewer.desk@vidyasetu.local", "COMPLIANCE_REVIEWER", "SIGNAL_REVIEW_DECISION", f"integrity_signals/{sig5.id}", {"decision": "RESOLVED_ACCEPTED", "notes": "Synthetic demo review: APAAR status is pending in the simulated adapter. No adverse conclusion is drawn. Await acknowledgement and recheck status"}),
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

    await session.commit()
    logger.info("Synthetic demo data successfully populated!")
    return True
