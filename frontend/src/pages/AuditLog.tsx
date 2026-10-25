import React, { useEffect, useState } from 'react';
import { History, ShieldCheck, Hash, RefreshCw, Key } from 'lucide-react';
import { AuditLogItem } from '../types';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const AuditLog: React.FC = () => {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = () => {
    setLoading(true);
    api
      .getAuditLogs()
      .then((res) => setLogs(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Cryptographic Immutable Audit Trail
            </h1>
            <MockBadge label="SHA-256 HASH CHAIN" />
          </div>
          <p className="text-xs text-slate-500">
            Stage 07: Non-repudiable audit ledger recording every batch ingestion, simulated verification handshake, and reviewer decision.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Trail
        </button>
      </div>

      {/* Ledger Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4">Actor & Role</th>
              <th className="py-3 px-4">Action</th>
              <th className="py-3 px-4">Resource Target</th>
              <th className="py-3 px-4">Cryptographic Hash (SHA-256)</th>
              <th className="py-3 px-4">Integrity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
            {loading ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-slate-400 font-sans">Loading audit records...</td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-12 text-center text-slate-400 font-sans">No audit records found.</td>
              </tr>
            ) : (
              logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-50/70">
                  <td className="py-3 px-4 text-slate-500 truncate max-w-xs">{log.timestamp}</td>
                  <td className="py-3 px-4">
                    <span className="text-slate-800 font-semibold">{log.actor}</span>
                    <span className="block text-[10px] text-slate-400">{log.role}</span>
                  </td>
                  <td className="py-3 px-4 font-bold text-blue-700">{log.action}</td>
                  <td className="py-3 px-4 text-slate-600 truncate max-w-xs">{log.resource}</td>
                  <td className="py-3 px-4 text-slate-500 text-[10px] truncate max-w-xs" title={log.tamper_hash}>
                    {log.tamper_hash}
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 font-sans">
                      <ShieldCheck className="w-3 h-3 text-emerald-600" />
                      Verified
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
