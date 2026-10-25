import React, { useState } from 'react';
import { Award, Search, CheckCircle2, ShieldCheck, Hash, Calendar, Building2 } from 'lucide-react';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const Verification: React.FC = () => {
  const [queryKey, setQueryKey] = useState('ENR-2025-CSE-001');
  const [result, setResult] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleVerify = async (key: string) => {
    if (!key.trim()) return;
    setLoading(true);
    setErrorMsg(null);
    setResult(null);

    try {
      const res = await api.verifyCredential(key.trim());
      setResult(res.credential);
    } catch (err: any) {
      setErrorMsg(err.message || 'Credential verification lookup failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Public Enrolment & Credential Verification Portal
            </h1>
            <MockBadge label="VERIFICATION SERVICE" />
          </div>
          <p className="text-xs text-slate-500">
            Stage 07: Validate authentic technical education enrolment status against cryptographic ledger anchors.
          </p>
        </div>
      </div>

      {/* Verification Lookup Input */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs max-w-2xl mx-auto space-y-4">
        <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
          Enter Student Enrolment Number or APAAR ID:
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. ENR-2025-CSE-001 or DEMO-APAAR-2026-904128"
            value={queryKey}
            onChange={(e) => setQueryKey(e.target.value)}
            className="flex-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 font-mono"
          />
          <button
            onClick={() => handleVerify(queryKey)}
            disabled={loading || !queryKey}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <Search className="w-3.5 h-3.5" />
            {loading ? 'Verifying...' : 'Verify Credential'}
          </button>
        </div>

        {/* Quick Demo Links */}
        <div className="flex items-center gap-2 text-[11px] text-slate-500 pt-1">
          <span>Try Demo IDs:</span>
          <button
            onClick={() => {
              setQueryKey('ENR-2025-CSE-001');
              handleVerify('ENR-2025-CSE-001');
            }}
            className="text-blue-600 hover:underline font-mono"
          >
            ENR-2025-CSE-001
          </button>
          <span>•</span>
          <button
            onClick={() => {
              setQueryKey('DEMO-APAAR-2026-904129');
              handleVerify('DEMO-APAAR-2026-904129');
            }}
            className="text-blue-600 hover:underline font-mono"
          >
            DEMO-APAAR-2026-904129
          </button>
        </div>
      </div>

      {/* Error state */}
      {errorMsg && (
        <div className="max-w-2xl mx-auto p-4 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 text-center">
          {errorMsg}
        </div>
      )}

      {/* Certificate / Verification Card */}
      {result && (
        <div className="max-w-2xl mx-auto bg-white rounded-xl border-2 border-emerald-500/40 shadow-md p-6 space-y-5">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Verified Genuine Enrolment
                </span>
                <h3 className="text-base font-bold text-slate-900 mt-1">{result.student_name}</h3>
              </div>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-slate-400 block font-mono">Status</span>
              <span className="text-xs font-bold text-emerald-700">{result.integrity_standing}</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Enrolment Number</span>
              <span className="font-mono font-bold text-slate-800">{result.enrolment_number}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">APAAR ID</span>
              <span className="font-mono font-bold text-slate-800">{result.apaar_id}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Approved Institution</span>
              <span className="font-semibold text-slate-800">{result.institution_name}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <span className="text-slate-400 block text-[10px] uppercase font-semibold">Academic Programme</span>
              <span className="font-semibold text-slate-800">{result.programme}</span>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 space-y-1">
            <span className="text-[10px] text-slate-400 font-mono uppercase flex items-center gap-1 font-semibold">
              <Hash className="w-3 h-3 text-slate-400" />
              Cryptographic Enrolment Fingerprint (SHA-256)
            </span>
            <p className="font-mono text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200 break-all select-all">
              {result.cryptographic_fingerprint}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
