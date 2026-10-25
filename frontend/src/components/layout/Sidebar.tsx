import React from 'react';
import {
  LayoutDashboard,
  Building2,
  Users,
  UploadCloud,
  Fingerprint,
  Scale,
  ClipboardCheck,
  Award,
  FileBarChart2,
  History,
  Settings as SettingsIcon,
  ShieldCheck,
  ChevronRight,
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  reviewCount?: number;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  isDistinctStage?: boolean;
  stageBadge?: string;
  badgeCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, reviewCount = 0 }) => {
  const navItems: NavItem[] = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'institutions', label: 'Institutions', icon: Building2 },
    { id: 'students', label: 'Student Records', icon: Users },
    { id: 'intake', label: 'Data Intake', icon: UploadCloud },
    {
      id: 'apaar',
      label: 'APAAR Validation',
      icon: Fingerprint,
      isDistinctStage: true,
      stageBadge: 'Stage 3 (Mock)',
    },
    { id: 'integrity', label: 'Intake Integrity', icon: Scale },
    {
      id: 'review',
      label: 'Evidence & Review',
      icon: ClipboardCheck,
      badgeCount: reviewCount,
    },
    { id: 'verification', label: 'Verification', icon: Award },
    { id: 'reports', label: 'Reports', icon: FileBarChart2 },
    { id: 'audit', label: 'Audit Log', icon: History },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col flex-shrink-0 border-r border-slate-800 select-none min-h-screen">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-5 border-b border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-white tracking-tight text-base">VidyaSetu</span>
              <span className="text-[10px] uppercase font-semibold tracking-wider px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300 border border-blue-700/40">
                RegTech
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">AICTE Regulatory Suite</p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
          Enrolment Intelligence
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all group ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                  : item.isDistinctStage
                  ? 'text-cyan-200 hover:bg-slate-800/90 hover:text-white bg-slate-800/40 border border-cyan-500/20'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon
                  className={`w-4 h-4 transition-colors ${
                    isActive
                      ? 'text-white'
                      : item.isDistinctStage
                      ? 'text-cyan-400 group-hover:text-cyan-300'
                      : 'text-slate-400 group-hover:text-slate-200'
                  }`}
                />
                <span className="truncate">{item.label}</span>
              </div>

              <div className="flex items-center gap-1.5">
                {item.stageBadge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                      isActive
                        ? 'bg-blue-700 text-blue-100'
                        : 'bg-cyan-950 text-cyan-300 border border-cyan-800/60'
                    }`}
                  >
                    {item.stageBadge}
                  </span>
                )}
                {item.badgeCount !== undefined && item.badgeCount > 0 && (
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-500 text-slate-950">
                    {item.badgeCount}
                  </span>
                )}
                {!isActive && !item.stageBadge && !item.badgeCount && (
                  <ChevronRight className="w-3.5 h-3.5 text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Institutional Context & Disclaimer Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/30">
        <div className="bg-slate-800/60 rounded-lg p-2.5 border border-slate-700/50">
          <div className="flex items-center justify-between text-[11px] text-slate-300 mb-1">
            <span className="font-semibold text-white">SIH 2026 PS 26263</span>
            <span className="text-[9px] bg-amber-500/20 text-amber-300 px-1 py-0.2 rounded border border-amber-500/30 font-mono">
              DEMO MODE
            </span>
          </div>
          <p className="text-[10px] text-slate-400 leading-tight">
            Synthetic student records. Deterministic rule evaluation.
          </p>
        </div>
      </div>
    </aside>
  );
};
