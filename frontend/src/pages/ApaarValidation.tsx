import React, { useEffect, useState } from 'react';
import {
  Fingerprint,
  CheckCircle2,
  Clock,
  XCircle,
  HelpCircle,
  Search,
  Activity,
  ShieldCheck,
  Cpu,
} from 'lucide-react';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const ApaarValidation: React.FC = () => {
  const [adapterStatus, setAdapterStatus] = useState<any | null>(null);
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Interactive Simulator state
  const [lookupId, setLookupId] = useState('');
  const [lookupName, setLookupName] = useState('');
  const [lookupResult, setLookupResult] = useState<any | null>(null);
  const [lookupLoading, setLookupLoading] = useState(false);

  useEffect(() => {
    Promise.all([api.getApaarStatus(), api.getApaarRecords()])
      .then(([statusRes, recordsRes]) => {
        setAdapterStatus(statusRes);
        setRecords(recordsRes.data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleLookup = async (id: string, name: string) => {
    setLookupLoading(true);
    setLookupResult(null);
    try {
      const res = await api.lookupApaar(id, name);
      setLookupResult(res);
    } catch (err: any) {
      setLookupResult({ success: false, message: err.message });
    } finally {
      setLookupLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header - Highlighted as Visibly Distinct Workflow Stage */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-cyan-950 text-white rounded-xl p-6 border border-cyan-800/60 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-400/30 uppercase tracking-wider">
                Pipeline Stage 03 — Visibly Distinct Workflow Stage
              </span>
              <MockBadge label="SIMULATED ADAPTER" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              <Fingerprint className="w-5 h-5 text-cyan-400" />
              APAAR Identity Validation & Credit Registry Gateway
            </h1>
            <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
              Deterministic adapter interface simulating DigiLocker and Academic Bank of Credits (ABC) handshake protocols. Non-punitive identity verification under DPDP Act 2023 purpose limitation.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700 font-mono text-xs">
              <span className="text-slate-400 block text-[10px]">Adapter Latency</span>
              <span className="text-cyan-400 font-bold">~250ms (Mock Mode)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mandatory Regulatory Integrity Banner */}
      <div className="bg-cyan-50/70 border border-cyan-200/90 rounded-xl p-4 text-xs text-cyan-950 flex items-start gap-3">
        <ShieldCheck className="w-4 h-4 text-cyan-700 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="font-bold text-cyan-950">Statutory Privacy & Non-Punitive Notice:</span>
          <p className="text-cyan-900 leading-relaxed">
            • <strong>No Real PII / No Live APAAR Registry:</strong> All APAAR IDs and student records displayed are synthetic demo data.
            <br />
            • <strong>Missing or Pending Status ≠ Fraud:</strong> Pending APAAR sync is an operational transition state, not a compliance violation.
            <br />
            • <strong>Discrepancies = Review Signals:</strong> Name spelling variations generate human-in-the-loop review tickets rather than automated rejections.
          </p>
        </div>
      </div>

      {/* Two Column Layout: Adapter Telemetry & Interactive Single-ID Lookup Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Lookup Simulator */}
        <div className="lg:col-span-2 bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-600" />
              <h2 className="text-sm font-bold text-slate-900">
                Interactive APAAR Identity Handshake Simulator
              </h2>
            </div>
            <MockBadge label="TEST TOOL" />
          </div>
          <p className="text-xs text-slate-500">
            Test deterministic mock verification outcomes by submitting an APAAR ID and Student Name or choosing a demo scenario.
          </p>

          {/* Quick Demo Pre-sets */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-[11px] font-semibold text-slate-500">Preset Scenarios:</span>
            <button
              onClick={() => {
                setLookupId('DEMO-APAAR-2026-904128');
                setLookupName('Ananya Sharma');
                handleLookup('DEMO-APAAR-2026-904128', 'Ananya Sharma');
              }}
              className="px-2.5 py-1 text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md font-medium transition-colors"
            >
              1. Direct Match (Verified)
            </button>
            <button
              onClick={() => {
                setLookupId('DEMO-APAAR-2026-904133');
                setLookupName('Pooja V. Nair');
                handleLookup('DEMO-APAAR-2026-904133', 'Pooja V. Nair');
              }}
              className="px-2.5 py-1 text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md font-medium transition-colors"
            >
              2. Async Pending (Signal, Not Fraud)
            </button>
            <button
              onClick={() => {
                setLookupId('DEMO-APAAR-2026-904139');
                setLookupName('Aarav S. Verma');
                handleLookup('DEMO-APAAR-2026-904139', 'Aarav S. Verma');
              }}
              className="px-2.5 py-1 text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md font-medium transition-colors"
            >
              3. Spelling Variation (Mismatch)
            </button>
          </div>

          {/* Custom Input */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                APAAR Identifier (Mock)
              </label>
              <input
                type="text"
                placeholder="e.g. DEMO-APAAR-2026-904128"
                value={lookupId}
                onChange={(e) => setLookupId(e.target.value)}
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Student Name
              </label>
              <input
                type="text"
                placeholder="e.g. Ananya Sharma"
                value={lookupName}
                onChange={(e) => setLookupName(e.target.value)}
                className="w-full px-3 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
          </div>

          <button
            onClick={() => handleLookup(lookupId, lookupName)}
            disabled={lookupLoading || !lookupId}
            className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {lookupLoading ? 'Contacting Simulated APAAR Gateway...' : 'Execute Simulated Handshake'}
          </button>

          {/* Handshake Result Container */}
          {lookupResult && (
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-2 mt-3">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-800">Gateway Response Payload:</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                    lookupResult.status === 'VERIFIED'
                      ? 'bg-emerald-100 text-emerald-800'
                      : lookupResult.status === 'PENDING_VERIFICATION'
                      ? 'bg-cyan-100 text-cyan-800'
                      : 'bg-rose-100 text-rose-800'
                  }`}
                >
                  {lookupResult.status}
                </span>
              </div>
              <p className="text-slate-600">{lookupResult.message}</p>
              {lookupResult.token && (
                <div className="font-mono text-[11px] text-slate-500">
                  Verification Token: <span className="font-bold text-slate-700">{lookupResult.token}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Adapter Specs */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-xs flex flex-col justify-between">
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-cyan-600" />
              Adapter Configuration
            </h3>
            <div className="space-y-2 text-xs">
              <div className="p-2.5 bg-slate-50 rounded-lg">
                <span className="text-[10px] text-slate-400 block uppercase">Protocol</span>
                <span className="font-mono font-semibold text-slate-700">OAuth2 + Signed JWT (Mock)</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg">
                <span className="text-[10px] text-slate-400 block uppercase">Gateway URI</span>
                <span className="font-mono text-[11px] text-slate-600 break-all">
                  mock://apaar.digilocker.local/v1
                </span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg">
                <span className="text-[10px] text-slate-400 block uppercase">Regulatory Anchor</span>
                <span className="font-semibold text-slate-700">National Credit Framework (NCrF)</span>
              </div>
            </div>
          </div>
          <p className="text-[10px] text-slate-400 mt-4 leading-tight">
            Adapter simulates identity resolution with zero transmission of unhashed personal data.
          </p>
        </div>
      </div>

      {/* APAAR Stage Records Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Enrolment Records in APAAR Validation Stage
            </h3>
            <p className="text-[11px] text-slate-500">
              Live status of automated identity resolution handshake per student enrolment.
            </p>
          </div>
          <span className="font-mono text-xs font-semibold text-slate-600">
            {records.length} Monitored
          </span>
        </div>

        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
              <th className="py-3 px-4">Student Name</th>
              <th className="py-3 px-4">APAAR Identifier</th>
              <th className="py-3 px-4">Validation Status</th>
              <th className="py-3 px-4">Mock Gateway Code</th>
              <th className="py-3 px-4">Match Score</th>
              <th className="py-3 px-4">Explainable Remarks</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-400">Loading APAAR stage records...</td>
              </tr>
            ) : records.map((r) => (
              <tr key={r.student_id} className="hover:bg-slate-50/70">
                <td className="py-3 px-4 font-semibold text-slate-900">{r.student_name}</td>
                <td className="py-3 px-4 font-mono font-medium text-slate-700">{r.apaar_id}</td>
                <td className="py-3 px-4">
                  {r.apaar_status === 'VERIFIED' && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Verified
                    </span>
                  )}
                  {r.apaar_status === 'PENDING_VERIFICATION' && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-cyan-50 text-cyan-800 border border-cyan-200">
                      <Clock className="w-3 h-3 text-cyan-600" /> Pending Sync
                    </span>
                  )}
                  {r.apaar_status === 'MISMATCH' && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                      <XCircle className="w-3 h-3 text-rose-600" /> Mismatch
                    </span>
                  )}
                </td>
                <td className="py-3 px-4 font-mono text-[11px] text-slate-600">
                  {r.handshake?.mock_response_code}
                </td>
                <td className="py-3 px-4 font-mono font-bold text-slate-700">
                  {r.handshake?.identity_score !== null ? `${r.handshake?.identity_score}%` : 'N/A'}
                </td>
                <td className="py-3 px-4 text-slate-600 text-[11px] max-w-sm">
                  {r.handshake?.remarks}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
