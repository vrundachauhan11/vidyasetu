"""Initial schema for VidyaSetu

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-25 16:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Institutions table
    op.create_table(
        'institutions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('aicte_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('institution_type', sa.String(length=100), nullable=True, server_default='Engineering & Technology'),
        sa.Column('approval_status', sa.String(length=50), nullable=True, server_default='Approved'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_institutions_aicte_id', 'institutions', ['aicte_id'])

    # Programme Approvals table
    op.create_table(
        'programme_approvals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('institution_id', sa.String(length=36), sa.ForeignKey('institutions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('programme_name', sa.String(length=200), nullable=False),
        sa.Column('degree_level', sa.String(length=50), nullable=True, server_default='Undergraduate'),
        sa.Column('academic_year', sa.String(length=20), nullable=True, server_default='2025-26'),
        sa.Column('sanctioned_intake', sa.Integer(), nullable=False),
        sa.Column('approved_quota_details', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Student Enrolments table
    op.create_table(
        'student_enrolments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('institution_id', sa.String(length=36), sa.ForeignKey('institutions.id'), nullable=False),
        sa.Column('programme_id', sa.String(length=36), sa.ForeignKey('programme_approvals.id'), nullable=False),
        sa.Column('student_name', sa.String(length=150), nullable=False),
        sa.Column('apaar_id', sa.String(length=50), nullable=True),
        sa.Column('apaar_status', sa.String(length=50), nullable=True, server_default='PENDING_VERIFICATION'),
        sa.Column('dob', sa.String(length=20), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('quota', sa.String(length=100), nullable=True),
        sa.Column('enrolment_number', sa.String(length=100), nullable=True, unique=True),
        sa.Column('admission_date', sa.String(length=20), nullable=True),
        sa.Column('integrity_status', sa.String(length=50), nullable=True, server_default='CLEARED'),
        sa.Column('version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('is_latest', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_student_enrolments_apaar_id', 'student_enrolments', ['apaar_id'])
    op.create_index('ix_student_enrolments_enrolment_number', 'student_enrolments', ['enrolment_number'])

    # Intake Batches table
    op.create_table(
        'intake_batches',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('institution_id', sa.String(length=36), sa.ForeignKey('institutions.id'), nullable=False),
        sa.Column('batch_reference', sa.String(length=100), nullable=False, unique=True),
        sa.Column('academic_year', sa.String(length=20), nullable=True, server_default='2025-26'),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('total_records', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('valid_records', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('flagged_records', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='PROCESSED'),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    )

    # Integrity Signals table
    op.create_table(
        'integrity_signals',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('student_id', sa.String(length=36), sa.ForeignKey('student_enrolments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_code', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=True, server_default='MEDIUM'),
        sa.Column('finding_summary', sa.String(length=255), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column('review_status', sa.String(length=50), nullable=True, server_default='PENDING'),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('reviewer_decision', sa.String(length=50), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource', sa.String(length=150), nullable=False),
        sa.Column('details_json', sa.Text(), nullable=True),
        sa.Column('tamper_hash', sa.String(length=128), nullable=False),
    )
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('integrity_signals')
    op.drop_table('intake_batches')
    op.drop_table('student_enrolments')
    op.drop_table('programme_approvals')
    op.drop_table('institutions')
