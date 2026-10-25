"""SQLAlchemy 2.x Data Models for VidyaSetu Modular Monolith."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aicte_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    institution_type = Column(String(100), default="Engineering & Technology")
    approval_status = Column(String(50), default="Approved")
    created_at = Column(DateTime, default=utc_now)

    programmes = relationship("ProgrammeApproval", back_populates="institution", cascade="all, delete-orphan")
    students = relationship("StudentEnrolment", back_populates="institution")
    batches = relationship("IntakeBatch", back_populates="institution")


class ProgrammeApproval(Base):
    __tablename__ = "programme_approvals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_id = Column(String(36), ForeignKey("institutions.id"), nullable=False)
    programme_name = Column(String(200), nullable=False)
    degree_level = Column(String(50), default="Undergraduate")
    academic_year = Column(String(20), default="2025-26")
    sanctioned_intake = Column(Integer, nullable=False)
    approved_quota_details = Column(String(255), default="State Quota 85%, Management Quota 15%")
    created_at = Column(DateTime, default=utc_now)

    institution = relationship("Institution", back_populates="programmes")
    students = relationship("StudentEnrolment", back_populates="programme")


class StudentEnrolment(Base):
    __tablename__ = "student_enrolments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_id = Column(String(36), ForeignKey("institutions.id"), nullable=False)
    programme_id = Column(String(36), ForeignKey("programme_approvals.id"), nullable=False)
    
    student_name = Column(String(150), nullable=False)
    apaar_id = Column(String(50), index=True, nullable=True)  # DEMO/SYNTHETIC only
    apaar_status = Column(String(50), default="PENDING_VERIFICATION")  # VERIFIED, PENDING_VERIFICATION, UNAVAILABLE, MISMATCH
    dob = Column(String(20), nullable=False)
    gender = Column(String(20), default="Female")
    category = Column(String(50), default="General")
    quota = Column(String(100), default="State Merit Quota")
    enrolment_number = Column(String(100), unique=True, index=True)
    admission_date = Column(String(20), default="2025-08-14")
    
    # Review signal flags (signals != fraud)
    integrity_status = Column(String(50), default="CLEARED")  # CLEARED, FLAGGED_FOR_REVIEW, UNDER_REVIEW, RESOLVED
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    institution = relationship("Institution", back_populates="students")
    programme = relationship("ProgrammeApproval", back_populates="students")
    signals = relationship("IntegritySignal", back_populates="student", cascade="all, delete-orphan")


class IntakeBatch(Base):
    __tablename__ = "intake_batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    institution_id = Column(String(36), ForeignKey("institutions.id"), nullable=False)
    batch_reference = Column(String(100), unique=True, nullable=False)
    academic_year = Column(String(20), default="2025-26")
    filename = Column(String(255), nullable=False)
    total_records = Column(Integer, default=0)
    valid_records = Column(Integer, default=0)
    flagged_records = Column(Integer, default=0)
    status = Column(String(50), default="PROCESSED")  # PROCESSED, REVIEW_REQUIRED, COMPLETED
    uploaded_at = Column(DateTime, default=utc_now)

    institution = relationship("Institution", back_populates="batches")


class IntegritySignal(Base):
    __tablename__ = "integrity_signals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("student_enrolments.id"), nullable=False)
    rule_code = Column(String(50), nullable=False)
    severity = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH
    finding_summary = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    review_status = Column(String(50), default="PENDING")  # PENDING, ACCEPTED, OVERRULED, CORRECTION_SUBMITTED
    reviewer_notes = Column(Text, nullable=True)
    reviewer_decision = Column(String(50), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    student = relationship("StudentEnrolment", back_populates="signals")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=utc_now, index=True)
    actor = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    resource = Column(String(150), nullable=False)
    details_json = Column(Text, nullable=True)
    tamper_hash = Column(String(128), nullable=False)
