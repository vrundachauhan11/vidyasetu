import React from 'react';
import {
  Building2,
  Users,
  Fingerprint,
  AlertTriangle,
  History,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldCheck,
  FileSpreadsheet,
  HelpCircle,
} from 'lucide-react';
import { DashboardData } from '../types';
import { MockBadge } from '../components/layout/MockBadge';

interface OverviewProps {
  data: DashboardData | null;
  loading: boolean;
  onNavigate: (tab: string) => void;
}

export const Overview: React.FC<OverviewProps> = ({ data, loading, onNavigate }) => {
  if (loading && !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-3">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-sm text-slate-500 font-medium">Loading VidyaSetu Regulatory Telemetry...</p>
        </div>
      </div>
    );
  }

  const metrics = data?.metrics || {
    total_institutions: 3,
    total_students: 5,
    apaar_verified_pct: 60.0,
    total_verified: 3,
    total_pending_apaar: 1,
    total_mismatch_apaar: 1,
    active_signals: 3,
    total_audit_logs: 4,
  };

  const workflowStages = data?.workflow_stages || [];
  const recentBatches = data?.recent_batches || [];
  const recentSignals = data?.recent_signals || [];

  return (
    <div className="space-y-6">
      {/* Top Banner / Heading */}
      <div className="bg-white rounded-xl p-6 border border-slate-200/80 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              AICTE Enrolment Integrity & Regulatory Overview
            </h1>
            <MockBadge label="DEMO TELEMETRY" />
          </div>
          <p className="text-xs text-slate-500 max-w-2xl">
            National regulatory oversight portal for technical institutions. Transparent, deterministic rule evaluation aligned with AICTE Approval Process Handbook (APH) and DPDP Act 2023.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('intake')}
            className="px-3.5 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-xs transition-colors flex items-center gap-1.5"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            Upload New Batch CSV
          </button>
          <button
            onClick={() => onNavigate('review')}
            className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg border border-slate-200 transition-colors flex items-center gap-1.5"
          >
            Review Queue ({metrics.active_signals})
          </button>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Institutions */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Approved Institutions
            </span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <Building2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">{metrics.total_institutions}</div>
            <div className="flex items-center justify-between text-xs text-slate-500 mt-1">
              <span>Technical & Management</span>
              <span className="text-blue-600 font-medium">100% Audited</span>
            </div>
          </div>
        </div>

        {/* Card 2: Student Enrolments */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Enrolment Records
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-slate-900">{metrics.total_students}</div>
            <div className="flex items-center justify-between text-xs text-slate-500 mt-1">
              <span>Synthetic Roster</span>
              <span className="text-emerald-700 font-medium">AY 2025-26</span>
            </div>
          </div>
        </div>

        {/* Card 3: APAAR Match Ratio */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              APAAR Verified Rate
            </span>
            <div className="w-8 h-8 rounded-lg bg-cyan-50 text-cyan-700 flex items-center justify-center">
              <Fingerprint className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-slate-900">{metrics.apaar_verified_pct}%</span>
              <span className="text-xs text-slate-500 font-mono">
                ({metrics.total_verified}/{metrics.total_students})
              </span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-500 mt-1">
              <span>Simulated Handshake</span>
              <span className="text-cyan-700 font-medium font-mono">{metrics.total_pending_apaar} Pending</span>
            </div>
          </div>
        </div>

        {/* Card 4: Integrity Signals */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Active Review Signals
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-amber-600">{metrics.active_signals}</div>
            <div className="flex items-center justify-between text-xs text-slate-500 mt-1">
              <span>Requires Human Triage</span>
              <span className="text-amber-700 font-medium font-mono">Non-punitive</span>
            </div>
          </div>
        </div>
      </div>

      {/* Regulatory Principles Notice */}
      <div className="bg-blue-50/70 border border-blue-200/80 rounded-xl p-4 text-xs text-blue-900 flex items-start gap-3">
        <HelpCircle className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <span className="font-semibold text-blue-950">Guiding Regulatory Principles:</span>
          <p className="text-blue-800 leading-relaxed">
            1. An integrity signal is a <strong>review flag</strong> for institutional verification, <strong>never a presumption of fraud</strong>.
            2. Missing or pending APAAR status is an operational onboarding state, not a disciplinary infraction.
            3. All verification findings are deterministic and explainable with statutory reference to the AICTE Approval Process Handbook.
          </p>
        </div>
      </div>

      {/* Seven-Stage Workflow Telemetry Section */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-slate-900">
                Seven-Stage Enrolment Integrity Pipeline
              </h2>
              <span className="text-[10px] px-2 py-0.5 rounded font-mono font-semibold bg-blue-100 text-blue-800">
                End-to-End Architecture
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Deterministic validation lifecycle from institutional CSV ingestion to immutable cryptographic audit log.
            </p>
          </div>
        </div>

        {/* Workflow Diagram Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {workflowStages.map((stage) => {
            const isApaar = stage.stage_number === 3;
            const isReview = stage.stage_number === 6;

            return (
              <div
                key={stage.stage_number}
                className={`p-4 rounded-lg border text-left flex flex-col justify-between transition-all ${
                  isApaar
                    ? 'bg-cyan-50/50 border-cyan-300 ring-1 ring-cyan-400/20 shadow-xs'
                    : isReview
                    ? 'bg-amber-50/40 border-amber-300'
                    : 'bg-slate-50/80 border-slate-200 hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-mono font-bold text-slate-500">
                      STAGE 0{stage.stage_number}
                    </span>
                    <span
                      className={`text-[9px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                        isApaar
                          ? 'bg-cyan-100 text-cyan-800'
                          : isReview
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-slate-200 text-slate-700'
                      }`}
                    >
                      {stage.badge}
                    </span>
                  </div>
                  <h3 className="text-xs font-bold text-slate-800 mb-1 leading-snug">
                    {stage.name}
                  </h3>
                  <p className="text-[11px] text-slate-500 leading-relaxed mb-3">
                    {stage.description}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-xs">
                  <span className="text-[10px] text-slate-400 font-medium">Status</span>
                  <span className="font-mono text-[11px] font-semibold text-slate-700">
                    {stage.status}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Two Column Section: Recent Batches & Active Signals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Batches */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900">Recent Data Intake Batches</h3>
            </div>
            <button
              onClick={() => onNavigate('intake')}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
            >
              View Intake Desk <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="divide-y divide-slate-100 overflow-hidden">
            {recentBatches.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">No intake batches processed yet.</p>
            ) : (
              recentBatches.map((b) => (
                <div key={b.id} className="py-3 flex items-center justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-slate-800">
                        {b.reference}
                      </span>
                      <span
                        className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
                          b.status === 'COMPLETED'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}
                      >
                        {b.status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 truncate max-w-xs">{b.filename}</p>
                  </div>
                  <div className="text-right text-xs">
                    <span className="font-bold text-slate-800">{b.total_records}</span>
                    <span className="text-slate-400 ml-1">records</span>
                    {b.flagged_records > 0 && (
                      <p className="text-[10px] text-amber-600 font-medium">
                        {b.flagged_records} signals flagged
                      </p>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Active Review Signals */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-500" />
              <h3 className="text-sm font-bold text-slate-900">Pending Review Triage Queue</h3>
            </div>
            <button
              onClick={() => onNavigate('review')}
              className="text-xs text-amber-600 hover:text-amber-800 font-medium flex items-center gap-1"
            >
              Open Review Desk <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="divide-y divide-slate-100">
            {recentSignals.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">No pending signals in review queue.</p>
            ) : (
              recentSignals.map((sig) => (
                <div key={sig.id} className="py-3 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${
                          sig.severity === 'HIGH'
                            ? 'bg-rose-100 text-rose-800 border border-rose-200'
                            : sig.severity === 'MEDIUM'
                            ? 'bg-amber-100 text-amber-800 border border-amber-200'
                            : 'bg-blue-100 text-blue-800 border border-blue-200'
                        }`}
                      >
                        {sig.severity}
                      </span>
                      <span className="text-xs font-semibold text-slate-800 font-mono">
                        {sig.rule_code}
                      </span>
                    </div>
                    <span className="text-xs text-slate-500">{sig.student_name}</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-snug">{sig.finding_summary}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
