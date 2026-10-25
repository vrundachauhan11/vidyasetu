import React, { useEffect, useState } from 'react';
import { Scale, ShieldCheck, AlertTriangle, BookOpen, ExternalLink, ArrowRight } from 'lucide-react';
import { RuleDefinition, IntegritySignalItem } from '../types';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

interface IntakeIntegrityProps {
  onNavigateToReview?: () => void;
}

export const IntakeIntegrity: React.FC<IntakeIntegrityProps> = ({ onNavigateToReview }) => {
  const [rules, setRules] = useState<RuleDefinition[]>([]);
  const [signals, setSignals] = useState<IntegritySignalItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getRules(), api.getSignals()])
      .then(([rulesRes, signalsRes]) => {
        setRules(rulesRes.data);
        setSignals(signalsRes.data);
      })
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
              Deterministic Intake Integrity Rule Registry
            </h1>
            <MockBadge label="RULE ENGINE" />
          </div>
          <p className="text-xs text-slate-500">
            Stages 4 & 5: Statutory AICTE rule catalog evaluating intake capacities, quota ceilings, and enrolment exclusivity with 100% deterministic explainability.
          </p>
        </div>

        {onNavigateToReview && (
          <button
            onClick={onNavigateToReview}
            className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors shadow-xs"
          >
            <AlertTriangle className="w-4 h-4" />
            Go to Review Queue ({signals.length})
          </button>
        )}
      </div>

      {/* Rules Catalog Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-3 text-center py-12 text-xs text-slate-400">Loading rule registry...</div>
        ) : (
          rules.map((rule) => {
            const firingCount = signals.filter((s) => s.rule_code === rule.code).length;

            return (
              <div
                key={rule.code}
                className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="font-mono font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200/60">
                      {rule.code}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                        rule.severity === 'HIGH'
                          ? 'bg-rose-100 text-rose-800'
                          : rule.severity === 'MEDIUM'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {rule.severity} Severity
                    </span>
                  </div>

                  <h3 className="text-xs font-bold text-slate-900 leading-snug">{rule.title}</h3>
                  <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                    {rule.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 space-y-1.5 text-[11px]">
                  <div className="flex items-center justify-between text-slate-500">
                    <span className="flex items-center gap-1">
                      <BookOpen className="w-3 h-3 text-slate-400" /> Statutory Clause
                    </span>
                    <span className="font-mono text-slate-700 text-[10px] truncate max-w-xs" title={rule.regulatory_reference}>
                      {rule.regulatory_reference}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-slate-500">
                    <span>Active Signals</span>
                    <span className={`font-mono font-bold ${firingCount > 0 ? 'text-amber-600' : 'text-slate-400'}`}>
                      {firingCount} Records
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Active Signals Explainable Log */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Explainable Rule Findings (Active Signals)
            </h3>
            <p className="text-[11px] text-slate-500">
              Clear mathematical / statutory justification generated for each review flag.
            </p>
          </div>
          <span className="text-xs font-mono font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
            {signals.length} Signals
          </span>
        </div>

        <div className="divide-y divide-slate-100">
          {signals.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-400">No active signals found.</div>
          ) : (
            signals.map((sig) => (
              <div key={sig.id} className="p-4 space-y-2 hover:bg-slate-50/60 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded ${
                        sig.severity === 'HIGH'
                          ? 'bg-rose-100 text-rose-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {sig.rule_code}
                    </span>
                    <span className="font-semibold text-xs text-slate-900">
                      {sig.student_name}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">({sig.enrolment_number})</span>
                  </div>

                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    Status: {sig.review_status}
                  </span>
                </div>

                <div className="text-xs text-slate-700 font-medium">
                  {sig.finding_summary}
                </div>

                <div className="text-xs text-slate-500 bg-slate-50 p-3 rounded-lg border border-slate-200/80 leading-relaxed font-sans">
                  <strong className="text-slate-700">Detailed Rule Explanation:</strong> {sig.explanation}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
