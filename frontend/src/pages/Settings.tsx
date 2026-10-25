import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Shield, Sliders, Database, Lock, Info } from 'lucide-react';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';

export const Settings: React.FC = () => {
  const [policies, setPolicies] = useState<any | null>(null);
  const [latency, setLatency] = useState(250);
  const [mockEnabled, setMockEnabled] = useState(true);

  useEffect(() => {
    api.getConsentPolicies().then((res) => setPolicies(res)).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Platform & Regulatory Settings
            </h1>
            <MockBadge label="ADMIN CONTROLS" />
          </div>
          <p className="text-xs text-slate-500">
            System configuration, simulated gateway parameters, and statutory DPDP Act 2023 purpose limitation registries.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulation Controls */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <Sliders className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">Simulation Adapter Parameters</h2>
          </div>

          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <div>
                <span className="font-semibold text-slate-800 block">Simulated APAAR Adapter</span>
                <span className="text-[11px] text-slate-500">Route calls to deterministic mock registry</span>
              </div>
              <input
                type="checkbox"
                checked={mockEnabled}
                onChange={(e) => setMockEnabled(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
              />
            </div>

            <div className="p-3 bg-slate-50 rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-800">Simulated Adapter Latency</span>
                <span className="font-mono font-bold text-blue-600">{latency} ms</span>
              </div>
              <input
                type="range"
                min="50"
                max="1000"
                step="50"
                value={latency}
                onChange={(e) => setLatency(Number(e.target.value))}
                className="w-full accent-blue-600"
              />
              <span className="text-[10px] text-slate-400 block">
                Adjust simulated network latency for interactive demonstration.
              </span>
            </div>
          </div>
        </div>

        {/* Database & Environment Info */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <Database className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">Deployment & Environment Metadata</h2>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500">Application Name:</span>
              <span className="font-semibold text-slate-800 font-mono">VidyaSetu</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500">Version:</span>
              <span className="font-semibold text-slate-800 font-mono">0.1.0-alpha</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500">Problem Statement:</span>
              <span className="font-semibold text-slate-800 font-mono">SIH 2026 PS 26263</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500">Database Engine:</span>
              <span className="font-semibold text-slate-800 font-mono">PostgreSQL / SQLite Dual-Support</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-500">ORM / Migration:</span>
              <span className="font-semibold text-slate-800 font-mono">SQLAlchemy 2.x + Alembic</span>
            </div>
          </div>
        </div>
      </div>

      {/* DPDP Act 2023 Statutory Purpose Notices */}
      <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
          <Shield className="w-4 h-4 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-900">
            Digital Personal Data Protection (DPDP) Act 2023 — Purpose Limitation Registry
          </h2>
        </div>

        <p className="text-xs text-slate-600 leading-relaxed">
          {policies?.purpose_specification || 'Processing of student enrolment records is strictly limited to regulatory compliance and verification of approved intake limits.'}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
          {policies?.policies?.map((pol: any) => (
            <div key={pol.purpose_code} className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1">
              <span className="font-mono font-bold text-blue-700 block text-[10px]">{pol.purpose_code}</span>
              <span className="font-semibold text-slate-800 block">{pol.description}</span>
              <span className="text-[11px] text-slate-500 block">Consent: {pol.consent_required}</span>
              <span className="text-[10px] text-slate-400 block pt-1">Retention: {pol.retention_period}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
