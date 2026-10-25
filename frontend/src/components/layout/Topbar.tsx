import React from 'react';
import {
  Activity,
  UserCheck,
  Search,
  Bell,
  Sparkles,
  Info,
} from 'lucide-react';
import { RoleType, UserProfile } from '../../types';

interface TopbarProps {
  currentUser: UserProfile | null;
  onSwitchRole: (role: RoleType) => void;
  isBackendHealthy: boolean;
}

export const Topbar: React.FC<TopbarProps> = ({
  currentUser,
  onSwitchRole,
  isBackendHealthy,
}) => {
  const roles: { id: RoleType; label: string }[] = [
    { id: 'REGULATOR_AICTE', label: 'AICTE Council Regulator' },
    { id: 'INSTITUTION_ADMIN', label: 'Institution Registrar' },
    { id: 'COMPLIANCE_REVIEWER', label: 'Compliance Reviewer' },
    { id: 'AUDITOR', label: 'Regulatory Auditor' },
  ];

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      {/* Search & Breadcrumb info */}
      <div className="flex items-center gap-4 w-96">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search student APAAR, enrolment #, or institution..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all text-slate-700 placeholder:text-slate-400"
          />
        </div>
      </div>

      {/* Center banner: DEMO DATA / SIMULATION pill */}
      <div className="hidden lg:flex items-center gap-2 px-3 py-1 bg-amber-50 border border-amber-200/70 rounded-full text-xs text-amber-900 font-medium">
        <Info className="w-3.5 h-3.5 text-amber-600" />
        <span>DEMO DATA ONLY</span>
        <span className="text-amber-400">•</span>
        <span className="text-amber-700 font-normal">APAAR & AICTE Registries are Simulated</span>
      </div>

      {/* Right controls: Role switcher, System status & User badge */}
      <div className="flex items-center gap-3">
        {/* Backend health status pill */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
            isBackendHealthy
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : 'bg-rose-50 text-rose-700 border-rose-200'
          }`}
          title={isBackendHealthy ? 'API & Database Connected' : 'Checking API connection...'}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              isBackendHealthy ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
            }`}
          />
          <span className="font-mono text-[11px]">
            {isBackendHealthy ? 'Backend: Online' : 'Backend: Degraded'}
          </span>
        </div>

        {/* Role Selector dropdown */}
        <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-lg border border-slate-200">
          <UserCheck className="w-3.5 h-3.5 text-slate-500 ml-1.5" />
          <select
            value={currentUser?.role || 'REGULATOR_AICTE'}
            onChange={(e) => onSwitchRole(e.target.value as RoleType)}
            className="bg-transparent text-xs font-medium text-slate-700 focus:outline-none pr-1 py-0.5 cursor-pointer"
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.label}
              </option>
            ))}
          </select>
        </div>

        {/* User profile capsule */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-blue-100 border border-blue-200 flex items-center justify-center text-blue-700 font-semibold text-xs">
            {currentUser ? currentUser.name.charAt(0) : 'U'}
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-slate-800 leading-none">
              {currentUser?.name || 'Council Reviewer'}
            </p>
            <p className="text-[10px] text-slate-500 font-mono mt-0.5">
              {currentUser?.role || 'REGULATOR_AICTE'}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};
