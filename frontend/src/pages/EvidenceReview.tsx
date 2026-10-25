import React, { useEffect, useState } from 'react';
import { ClipboardCheck, CheckCircle2, XCircle, FileSearch, ShieldCheck, AlertCircle, RefreshCw } from 'lucide-react';
import { IntegritySignalItem } from '../types';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const EvidenceReview: React.FC = () => {
  const [queue, setQueue] = useState<IntegritySignalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [submittingId, setSubmittingId] = useState<string | null>(null);
  const [notes, setNotes] = useState<{ [key: string]: string }>({});
  const [lastActionResponse, setLastActionResponse] = useState<any | null>(null);

  const fetchQueue = () => {
    setLoading(true);
    api
      .getReviewQueue()
      .then((res) => setQueue(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleDecision = async (signalId: string, decision: string) => {
    setSubmittingId(signalId);
    setLastActionResponse(null);

    const reviewerNotes = notes[signalId] || `Reviewer action: ${decision}. Verified against institutional evidence roster.`;

    try {
      const res = await api.submitReviewDecision(signalId, decision, reviewerNotes);
      setLastActionResponse(res);
      fetchQueue();
    } catch (err: any) {
      alert(`Decision submission failed: ${err.message}`);
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Evidence Triage & Human Reviewer Desk
            </h1>
            <MockBadge label="STAGE 06: HUMAN-IN-THE-LOOP" />
          </div>
          <p className="text-xs text-slate-500">
            Adjudicate flagged enrolment signals with institutional justifications, secondary document verification, or correction mandates.
          </p>
        </div>

        <button
          onClick={fetchQueue}
          className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Queue ({queue.length})
        </button>
      </div>

      {/* Confirmation Alert after action */}
      {lastActionResponse && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 flex items-start gap-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold">Reviewer Decision Recorded & Stamped to Audit Trail</span>
            <p>{lastActionResponse.message}</p>
            <p className="font-mono text-[11px] text-emerald-800">
              Cryptographic SHA-256 Hash: <code className="bg-emerald-100/80 px-1 py-0.5 rounded">{lastActionResponse.tamper_hash}</code>
            </p>
          </div>
        </div>
      )}

      {/* Review Queue Items */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-16 text-xs text-slate-400">Loading pending review items...</div>
        ) : queue.length === 0 ? (
          <div className="bg-white rounded-xl p-12 border border-slate-200 text-center space-y-2">
            <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-800">Review Queue is Clear!</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              All active intake signals have been reviewed and adjudicated. New batch uploads will populate here if rules trigger review flags.
            </p>
          </div>
        ) : (
          queue.map((item) => {
            const isSubmitting = submittingId === item.id;

            return (
              <div
                key={item.id}
                className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4 hover:border-slate-300 transition-all"
              >
                {/* Header info */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 pb-3 border-b border-slate-100">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                          item.severity === 'HIGH'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {item.severity} PRIORITY
                      </span>
                      <span className="font-mono text-xs font-bold text-slate-700">
                        {item.rule_code}
                      </span>
                    </div>
                    <h2 className="text-sm font-bold text-slate-900 leading-snug">
                      {item.finding_summary}
                    </h2>
                  </div>

                  <div className="text-right text-xs">
                    <div className="font-bold text-slate-800">{item.student_name}</div>
                    <div className="text-slate-400 font-mono text-[11px]">
                      Enrolment: {item.enrolment_number} • APAAR: {item.apaar_id}
                    </div>
                  </div>
                </div>

                {/* Explanation block */}
                <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200/80 text-xs text-slate-600 space-y-1">
                  <span className="font-semibold text-slate-800 block">Deterministic Engine Analysis:</span>
                  <p className="leading-relaxed">{item.explanation}</p>
                </div>

                {/* Reviewer Note Input */}
                <div>
                  <label className="block text-[11px] font-semibold text-slate-700 mb-1">
                    Reviewer Justification & Adjudication Notes:
                  </label>
                  <input
                    type="text"
                    placeholder="Enter compliance rationale, supporting certificate reference, or quota adjustment details..."
                    value={notes[item.id] || ''}
                    onChange={(e) => setNotes({ ...notes, [item.id]: e.target.value })}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  />
                </div>

                {/* Action Buttons */}
                <div className="pt-2 flex flex-wrap items-center justify-end gap-2.5">
                  <button
                    onClick={() => handleDecision(item.id, 'DOCUMENT_VERIFIED')}
                    disabled={isSubmitting}
                    className="px-3.5 py-2 text-xs font-semibold text-cyan-800 bg-cyan-50 hover:bg-cyan-100 border border-cyan-200 rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <FileSearch className="w-3.5 h-3.5" />
                    Verify Secondary Certificate
                  </button>

                  <button
                    onClick={() => handleDecision(item.id, 'RESOLVED_OVERRULED')}
                    disabled={isSubmitting}
                    className="px-3.5 py-2 text-xs font-semibold text-rose-800 bg-rose-50 hover:bg-rose-100 border border-rose-200 rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Overrule (Require Correction)
                  </button>

                  <button
                    onClick={() => handleDecision(item.id, 'RESOLVED_ACCEPTED')}
                    disabled={isSubmitting}
                    className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center gap-1.5 shadow-xs disabled:opacity-50"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {isSubmitting ? 'Recording Decision...' : 'Accept Institutional Justification'}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
