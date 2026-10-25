import React, { useEffect, useState } from 'react';
import { Users, Search, Filter, ShieldAlert, CheckCircle2, Clock, XCircle, Eye, Info, AlertCircle, History } from 'lucide-react';
import { StudentRecord } from '../types';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const StudentRecords: React.FC = () => {
  const [students, setStudents] = useState<StudentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [apaarFilter, setApaarFilter] = useState('');
  const [integrityFilter, setIntegrityFilter] = useState('');
  const [selectedStudent, setSelectedStudent] = useState<StudentRecord | null>(null);

  const fetchRecords = () => {
    setLoading(true);
    api
      .getStudents({
        apaar_status: apaarFilter || undefined,
        integrity_status: integrityFilter || undefined,
        search: searchTerm || undefined,
      })
      .then((res) => setStudents(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchRecords();
  }, [apaarFilter, integrityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchRecords();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Synthetic Student Enrolment Repository
            </h1>
            <MockBadge label="DEMO ROSTER" />
          </div>
          <p className="text-xs text-slate-500">
            Immutable versioned enrolment records cross-referenced with APAAR identity signals and statutory quotas.
          </p>
        </div>

        {/* Search & Filter Form */}
        <form onSubmit={handleSearchSubmit} className="flex flex-wrap items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search name, APAAR or Enr #"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 w-48"
            />
          </div>

          <select
            value={apaarFilter}
            onChange={(e) => setApaarFilter(e.target.value)}
            className="text-xs py-1.5 px-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none text-slate-700"
          >
            <option value="">All APAAR States</option>
            <option value="VERIFIED">Verified</option>
            <option value="PENDING_VERIFICATION">Pending (In Progress)</option>
            <option value="MISMATCH">Mismatch</option>
          </select>

          <select
            value={integrityFilter}
            onChange={(e) => setIntegrityFilter(e.target.value)}
            className="text-xs py-1.5 px-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none text-slate-700"
          >
            <option value="">All Integrity States</option>
            <option value="CLEARED">Cleared</option>
            <option value="FLAGGED_FOR_REVIEW">Flagged for Review</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          <button
            type="submit"
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg transition-colors"
          >
            Apply
          </button>
        </form>
      </div>

      {/* Notice Banner */}
      <div className="bg-amber-50/60 border border-amber-200/80 rounded-xl p-3.5 text-xs text-amber-900 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>
            <strong>Reminder:</strong> A review flag indicates an anomaly requiring verification (e.g. spelling discrepancy, intake cap check). It is not a disciplinary determination.
          </span>
        </div>
        <span className="font-mono text-[11px] text-amber-700 font-semibold">{students.length} Records</span>
      </div>

      {/* Records Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4">Student & Programme</th>
                <th className="py-3 px-4">Enrolment #</th>
                <th className="py-3 px-4">APAAR Identifier</th>
                <th className="py-3 px-4">APAAR Status</th>
                <th className="py-3 px-4">Integrity Status</th>
                <th className="py-3 px-4">Version</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    Loading synthetic student records...
                  </td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-400">
                    No student records match the selected filters.
                  </td>
                </tr>
              ) : (
                students.map((st) => (
                  <tr key={st.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{st.student_name}</div>
                      <div className="text-[11px] text-slate-500">
                        {st.programme_name} • {st.quota}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-slate-700">
                      {st.enrolment_number}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-600">
                      {st.apaar_id || <span className="text-slate-400 italic">Not Provided</span>}
                    </td>
                    <td className="py-3 px-4">
                      {st.apaar_status === 'VERIFIED' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          Verified
                        </span>
                      )}
                      {st.apaar_status === 'PENDING_VERIFICATION' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-cyan-50 text-cyan-800 border border-cyan-200">
                          <Clock className="w-3 h-3 text-cyan-600" />
                          Pending (Syncing)
                        </span>
                      )}
                      {st.apaar_status === 'MISMATCH' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-rose-50 text-rose-700 border border-rose-200">
                          <XCircle className="w-3 h-3 text-rose-600" />
                          Mismatch
                        </span>
                      )}
                      {st.apaar_status === 'UNAVAILABLE' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
                          <AlertCircle className="w-3 h-3 text-slate-500" />
                          Missing / Roster
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {st.integrity_status === 'CLEARED' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                          Cleared
                        </span>
                      )}
                      {st.integrity_status === 'FLAGGED_FOR_REVIEW' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200">
                          <ShieldAlert className="w-3 h-3 text-amber-600" />
                          Flagged
                        </span>
                      )}
                      {st.integrity_status === 'RESOLVED' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-blue-50 text-blue-700 border border-blue-200">
                          Resolved
                        </span>
                      )}
                      {st.integrity_status === 'DOCUMENT_VERIFIED' && (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                          Doc Verified
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                      v{st.version}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setSelectedStudent(st)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors font-medium text-xs"
                      >
                        <Eye className="w-3 h-3" />
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal / Drawer */}
      {selectedStudent && (() => {
        const activeSignals = selectedStudent.signals?.filter((s) => s.review_status === 'PENDING') || [];
        const resolvedSignals = selectedStudent.signals?.filter((s) => s.review_status !== 'PENDING') || [];

        return (
          <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 space-y-4 border border-slate-200 max-h-[88vh] overflow-y-auto">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">{selectedStudent.student_name}</h3>
                  <p className="text-xs text-slate-500 font-mono">Enrolment: {selectedStudent.enrolment_number}</p>
                </div>
                <button
                  onClick={() => setSelectedStudent(null)}
                  className="text-slate-400 hover:text-slate-600 p-1 rounded"
                >
                  ✕
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-2.5 bg-slate-50 rounded-lg">
                  <span className="text-slate-400 block text-[10px] uppercase">Programme</span>
                  <span className="font-semibold text-slate-800">{selectedStudent.programme_name}</span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg">
                  <span className="text-slate-400 block text-[10px] uppercase">APAAR ID</span>
                  <span className="font-mono font-semibold text-slate-800">
                    {selectedStudent.apaar_id || 'Not Provided'}
                  </span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg">
                  <span className="text-slate-400 block text-[10px] uppercase">Quota Category</span>
                  <span className="font-semibold text-slate-800">{selectedStudent.quota} ({selectedStudent.category})</span>
                </div>
                <div className="p-2.5 bg-slate-50 rounded-lg">
                  <span className="text-slate-400 block text-[10px] uppercase">Admission Date</span>
                  <span className="font-semibold text-slate-800">{selectedStudent.admission_date}</span>
                </div>
              </div>

              {/* Integrity Signals & Review History */}
              <div className="pt-2 space-y-3">
                {/* Active Signals Section */}
                {activeSignals.length > 0 ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                        <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                        Active Integrity Signals ({activeSignals.length})
                      </h4>
                      <span className="text-[10px] text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 font-medium">
                        Requires Triage
                      </span>
                    </div>
                    <div className="space-y-2">
                      {activeSignals.map((sig) => (
                        <div key={sig.id} className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg text-xs space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="font-mono font-bold text-amber-900">{sig.rule_code}</span>
                            <span
                              className={`font-semibold text-[10px] px-1.5 py-0.5 rounded ${
                                sig.severity === 'HIGH'
                                  ? 'bg-rose-100 text-rose-800'
                                  : sig.severity === 'MEDIUM'
                                  ? 'bg-amber-100 text-amber-800'
                                  : 'bg-blue-100 text-blue-800'
                              }`}
                            >
                              {sig.severity} Severity
                            </span>
                          </div>
                          <p className="text-amber-900 font-medium leading-snug">{sig.finding_summary}</p>
                          {sig.explanation && (
                            <p className="text-slate-600 text-[11px] leading-relaxed bg-white/80 p-2 rounded border border-amber-100">
                              {sig.explanation}
                            </p>
                          )}
                          {sig.created_at && (
                            <div className="text-[10px] text-slate-400 font-mono pt-0.5">
                              Logged: {new Date(sig.created_at).toLocaleString()}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="p-3 bg-emerald-50/80 border border-emerald-200 rounded-lg flex items-start gap-2.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <div>
                      <h5 className="text-xs font-semibold text-emerald-900">No Active Review Signals</h5>
                      <p className="text-[11px] text-emerald-700 leading-snug">
                        This student record currently has no pending integrity findings. Operational standing is cleared or resolved.
                      </p>
                    </div>
                  </div>
                )}

                {/* Resolved Historical Signals Section */}
                {resolvedSignals.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-slate-100">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                        <History className="w-3.5 h-3.5 text-blue-600" />
                        Resolution & Audit History ({resolvedSignals.length})
                      </h4>
                      <span className="text-[10px] text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200 font-medium">
                        Audit Trail
                      </span>
                    </div>
                    <div className="space-y-2">
                      {resolvedSignals.map((sig) => (
                        <div key={sig.id} className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-mono font-semibold text-slate-700">{sig.rule_code}</span>
                            <span className="font-semibold text-[10px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                              {sig.reviewer_decision || sig.review_status}
                            </span>
                          </div>
                          <p className="text-slate-700 leading-snug">{sig.finding_summary}</p>
                          {(sig.reviewer_notes || sig.reviewer_decision) && (
                            <div className="p-2.5 bg-blue-50/70 border border-blue-100 rounded text-[11px] space-y-1">
                              <div className="flex items-center justify-between text-blue-900 font-medium">
                                <span>Reviewer Determination:</span>
                                {sig.reviewed_at && (
                                  <span className="text-[10px] text-blue-600 font-mono">
                                    {new Date(sig.reviewed_at).toLocaleDateString()}
                                  </span>
                                )}
                              </div>
                              <p className="text-blue-800 italic">
                                "{sig.reviewer_notes || 'Institutional justification verified and accepted.'}"
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex justify-end">
                <button
                  onClick={() => setSelectedStudent(null)}
                  className="px-4 py-1.5 text-xs font-semibold bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
};
