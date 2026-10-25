import React, { useEffect, useState } from 'react';
import { FileBarChart2, Download, Printer, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const Reports: React.FC = () => {
  const [summary, setSummary] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getReportsSummary()
      .then((res) => setSummary(res))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Regulatory Intelligence & Compliance Reporting
            </h1>
            <MockBadge label="COUNCIL REPORT" />
          </div>
          <p className="text-xs text-slate-500">
            Consolidated scrutiny findings and national technical education enrolment metrics for AICTE oversight council.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => window.print()}
            className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors border border-slate-200"
          >
            <Printer className="w-3.5 h-3.5" /> Print Report
          </button>
        </div>
      </div>

      {loading || !summary ? (
        <div className="text-center py-16 text-xs text-slate-400">Loading regulatory report...</div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-slate-200">
            <div>
              <span className="font-mono text-[11px] font-bold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded">
                {summary.report_id}
              </span>
              <h2 className="text-lg font-bold text-slate-900 mt-2">{summary.title}</h2>
              <p className="text-xs text-slate-500">Academic Year: {summary.academic_year} • Prepared for: {summary.generated_for}</p>
            </div>
            <div className="text-right text-xs">
              <span className="text-slate-400 block">Classification</span>
              <span className="font-bold text-slate-800">Regulatory Scrutiny / Official Demo</span>
            </div>
          </div>

          {/* KPIs */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[10px] text-slate-400 font-semibold uppercase block">Institutions Audited</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{summary.kpis?.institutions_audited}</span>
            </div>
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[10px] text-slate-400 font-semibold uppercase block">Total Enrolments</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{summary.kpis?.total_students_enrolled}</span>
            </div>
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[10px] text-slate-400 font-semibold uppercase block">APAAR Match Rate</span>
              <span className="text-xl font-bold text-cyan-700 mt-1 block">{summary.kpis?.apaar_compliance_rate}</span>
            </div>
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[10px] text-slate-400 font-semibold uppercase block">Triage Actions Taken</span>
              <span className="text-xl font-bold text-emerald-700 mt-1 block">{summary.kpis?.resolved_triage_actions}</span>
            </div>
          </div>

          {/* Findings */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Statutory Finding Summaries
            </h3>
            <div className="space-y-3">
              {summary.regulatory_findings?.map((f: any, idx: number) => (
                <div key={idx} className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                  <div className="font-bold text-slate-900">{f.category}</div>
                  <p className="text-slate-700">{f.finding}</p>
                  <p className="text-blue-700 font-medium pt-1">Council Directive: {f.action}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
