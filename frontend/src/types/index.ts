export type RoleType = 'REGULATOR_AICTE' | 'INSTITUTION_ADMIN' | 'COMPLIANCE_REVIEWER' | 'AUDITOR';

export type ApaarStatus = 'VERIFIED' | 'PENDING_VERIFICATION' | 'UNAVAILABLE' | 'MISMATCH';

export type IntegrityStatus = 'CLEARED' | 'FLAGGED_FOR_REVIEW' | 'UNDER_REVIEW' | 'RESOLVED' | 'DOCUMENT_VERIFIED';

export type SignalSeverity = 'HIGH' | 'MEDIUM' | 'LOW';

export interface ProgrammeApproval {
  id: string;
  programme_name: string;
  degree_level: string;
  academic_year: string;
  sanctioned_intake: number;
  approved_quota_details: string;
}

export interface Institution {
  id: string;
  aicte_id: string;
  name: string;
  state: string;
  district: string;
  institution_type: string;
  approval_status: string;
  programmes?: ProgrammeApproval[];
}

export interface StudentRecord {
  id: string;
  student_name: string;
  apaar_id: string | null;
  apaar_status: ApaarStatus;
  dob: string;
  gender: string;
  category: string;
  quota: string;
  enrolment_number: string;
  admission_date: string;
  integrity_status: IntegrityStatus;
  version: number;
  institution_name?: string;
  programme_name?: string;
  signals?: {
    id: string;
    rule_code: string;
    severity: SignalSeverity;
    finding_summary: string;
    explanation?: string;
    review_status: string;
    reviewer_decision?: string;
    reviewer_notes?: string;
    reviewed_at?: string;
    created_at?: string;
  }[];
}

export interface IntakeBatch {
  id: string;
  reference: string;
  filename: string;
  academic_year: string;
  total_records: number;
  valid_records: number;
  flagged_records: number;
  status: string;
  uploaded_at: string;
}

export interface IntegritySignalItem {
  id: string;
  student_id: string;
  student_name: string;
  enrolment_number: string;
  apaar_id: string;
  rule_code: string;
  severity: SignalSeverity;
  finding_summary: string;
  explanation: string;
  review_status: string;
  reviewer_decision?: string;
  reviewer_notes?: string;
  created_at: string;
}

export interface WorkflowStage {
  stage_number: number;
  name: string;
  description: string;
  status: string;
  active_count: number;
  badge: string;
}

export interface DashboardMetrics {
  total_institutions: number;
  total_students: number;
  apaar_verified_pct: number;
  total_verified: number;
  total_pending_apaar: number;
  total_mismatch_apaar: number;
  active_signals: number;
  total_audit_logs: number;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  workflow_stages: WorkflowStage[];
  recent_batches: IntakeBatch[];
  recent_signals: IntegritySignalItem[];
}

export interface RuleDefinition {
  code: string;
  title: string;
  category: string;
  severity: SignalSeverity;
  regulatory_reference: string;
  description: string;
  status: string;
  implementation_status?: 'OPERATIONAL' | 'DEMO_SPECIFICATION';
  reference_status?: 'VERIFIED_STATUTORY' | 'DEMO_REFERENCE';
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  actor: string;
  role: string;
  action: string;
  resource: string;
  details_json: string;
  tamper_hash: string;
  tamper_status: string;
}

export interface UserProfile {
  user_id: string;
  email: string;
  name: string;
  role: RoleType;
  institution_id: string;
  permissions: string[];
}
