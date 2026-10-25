import React, { useEffect, useState } from 'react';
import { Settings as SettingsIcon, Shield, Sliders, Database, Lock, Info, UserCheck, Key, LogOut } from 'lucide-react';
import { api } from '../services/api';
import { MockBadge } from '../components/layout/MockBadge';
import { UserProfile } from '../types';

interface SettingsProps {
  currentUser?: UserProfile | null;
  onLogout?: () => void;
}

export const Settings: React.FC<SettingsProps> = ({ currentUser, onLogout }) => {
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

      {/* Active Session & RBAC Card */}
      {currentUser && (
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-blue-600" />
              <h2 className="text-sm font-bold text-slate-900">Active Authentication & Role Profile</h2>
            </div>
            {onLogout && (
              <button
                type="button"
                onClick={onLogout}
                className="px-3 py-1 bg-rose-50 hover:bg-rose-100 text-rose-700 text-xs font-semibold rounded-lg border border-rose-200 flex items-center gap-1.5 transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" /> Sign Out
              </button>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
            <div className="p-3 bg-slate-50 rounded-lg space-y-1">
              <span className="text-[10px] text-slate-400 font-mono uppercase block">Authenticated Persona</span>
              <span className="font-semibold text-slate-800 block">{currentUser.name}</span>
              <span className="text-[11px] text-slate-500 font-mono block">{currentUser.email}</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg space-y-1">
              <span className="text-[10px] text-slate-400 font-mono uppercase block">Assigned RBAC Role</span>
              <span className="font-bold text-blue-700 font-mono block">{currentUser.role}</span>
              <span className="text-[11px] text-slate-500 block">Scope: {currentUser.institution_id}</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg space-y-1">
              <span className="text-[10px] text-slate-400 font-mono uppercase block">Session Token Standard</span>
              <span className="font-semibold text-emerald-700 font-mono block">HMAC-SHA256 Bearer</span>
              <span className="text-[11px] text-slate-500 block">Validity: 480 min (8 hours)</span>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg space-y-1">
              <span className="text-[10px] text-slate-400 font-mono uppercase block">Security Notice</span>
              <span className="text-[11px] text-amber-700 font-medium block">Demo Credential Mode</span>
              <span className="text-[10px] text-slate-500 block">Safe prototype simulation for SIH PS 26263</span>
            </div>
          </div>

          <div className="pt-2">
            <span className="text-[11px] font-semibold text-slate-600 block mb-1.5">Granted RBAC Action Permissions:</span>
            <div className="flex flex-wrap gap-1.5">
              {currentUser.permissions.map((perm) => (
                <span
                  key={perm}
                  className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200/80 font-mono text-[10px]"
                >
                  {perm}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

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

            <div className="space-y-1.5 p-3 bg-slate-50 rounded-lg">
              <div className="flex justify-between">
                <span className="font-semibold text-slate-800">Simulated Network Latency</span>
                <span className="font-mono text-blue-600 font-bold">{latency} ms</span>
              </div>
              <input
                type="range"
                min="0"
                max="1000"
                step="50"
                value={latency}
                onChange={(e) => setLatency(Number(e.target.value))}
                className="w-full accent-blue-600"
              />
              <span className="text-[10px] text-slate-400 block">
                Simulates real-world API gateway round-trip delay to National Academic Depository.
              </span>
            </div>
          </div>
        </div>

        {/* Database & Architecture Summary */}
        <div className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-100">
            <Database className="w-4 h-4 text-blue-600" />
            <h2 className="text-sm font-bold text-slate-900">Architecture & Storage Tier</h2>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Architecture Pattern:</span>
              <span className="font-semibold text-slate-800">Modular Monolith</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Backend Runtime:</span>
              <span className="font-semibold text-slate-800 font-mono">FastAPI (Python 3.14)</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Frontend Stack:</span>
              <span className="font-semibold text-slate-800">React + TypeScript + Vite + Tailwind CSS</span>
            </div>
            <div className="flex justify-between py-1.5 border-b border-slate-50">
              <span className="text-slate-500">Database Engine:</span>
              <span className="font-semibold text-slate-800 font-mono">SQLite / PostgreSQL compatible</span>
            </div>
            <div className="flex justify-between py-1.5">
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
