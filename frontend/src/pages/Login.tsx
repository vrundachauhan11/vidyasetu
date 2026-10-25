import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Building2,
  ClipboardCheck,
  Scale,
  Eye,
  EyeOff,
  Lock,
  Mail,
  ArrowRight,
  Info,
  CheckCircle2,
  AlertTriangle,
  FileText,
} from 'lucide-react';
import { api } from '../services/api';
import { RoleType, UserProfile, DemoRoleInfo } from '../types';

interface LoginProps {
  onLoginSuccess: (user: UserProfile) => void;
  targetNotice?: string;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess, targetNotice }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'quick' | 'manual'>('quick');
  const [demoRoles, setDemoRoles] = useState<DemoRoleInfo[]>([]);

  useEffect(() => {
    // Fetch available demo roles and credentials from backend
    api.getRoles()
      .then(setDemoRoles)
      .catch((err) => {
        console.warn('Failed to load demo roles list:', err);
      });
  }, []);

  const handleQuickLogin = async (role: RoleType) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const resp = await api.login({ role });
      onLoginSuccess(resp.user);
    } catch (err: any) {
      setErrorMsg(err.message || 'Login failed. Please verify the backend service is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setErrorMsg('Please enter both your institutional email and demo password.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    try {
      const resp = await api.login({ email, password });
      onLoginSuccess(resp.user);
    } catch (err: any) {
      setErrorMsg(err.message || 'Invalid demo credentials. Please check your email or password.');
    } finally {
      setLoading(false);
    }
  };

  const fillCredentials = (roleEmail: string, rolePassword: string) => {
    setEmail(roleEmail);
    setPassword(rolePassword);
    setActiveTab('manual');
    setErrorMsg(null);
  };

  const roleIcons: Record<string, React.ComponentType<{ className?: string }>> = {
    INSTITUTION_ADMIN: Building2,
    COMPLIANCE_REVIEWER: ClipboardCheck,
    REGULATOR_AICTE: Scale,
    AUDITOR: FileText,
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between font-sans selection:bg-blue-600 selection:text-white">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white shadow-lg shadow-blue-500/25">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white tracking-tight text-lg">VidyaSetu</span>
              <span className="text-[10px] uppercase font-semibold tracking-wider px-2 py-0.5 rounded bg-blue-900/70 text-blue-300 border border-blue-700/50">
                RegTech Prototype
              </span>
            </div>
            <p className="text-xs text-slate-400">AICTE Enrolment Integrity & Regulatory Intelligence Platform</p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-slate-300 font-mono text-[11px]">
            SIH 2026 PS 26263
          </span>
          <span className="hidden sm:inline-flex px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 font-medium text-[11px]">
            Demonstration Mode
          </span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 flex items-center justify-center p-6 md:p-10">
        <div className="w-full max-w-3xl">
          {/* Target Notification banner if redirected */}
          {targetNotice && (
            <div className="mb-6 p-3.5 bg-amber-950/40 border border-amber-800/60 rounded-xl flex items-center gap-3 text-amber-200 text-xs">
              <Info className="w-4 h-4 text-amber-400 shrink-0" />
              <span>{targetNotice}</span>
            </div>
          )}

          {/* Authentication Card */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-2xl shadow-black/60 overflow-hidden backdrop-blur-xl">
            {/* Card Header */}
            <div className="p-6 md:p-8 border-b border-slate-800/80 bg-slate-900/50">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                  <h1 className="text-xl md:text-2xl font-bold text-white tracking-tight">
                    Institutional Access & Regulatory Sign-In
                  </h1>
                  <p className="text-xs md:text-sm text-slate-400 mt-1">
                    Select a designated demonstration role or authenticate using synthetic demo credentials.
                  </p>
                </div>

                {/* Tab Switcher */}
                <div className="flex items-center p-1 bg-slate-950/70 rounded-xl border border-slate-800 shrink-0">
                  <button
                    type="button"
                    onClick={() => { setActiveTab('quick'); setErrorMsg(null); }}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                      activeTab === 'quick'
                        ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    1-Click Personas
                  </button>
                  <button
                    type="button"
                    onClick={() => { setActiveTab('manual'); setErrorMsg(null); }}
                    className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
                      activeTab === 'manual'
                        ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Credential Input
                  </button>
                </div>
              </div>
            </div>

            {/* Error Message Alert */}
            {errorMsg && (
              <div className="mx-6 md:mx-8 mt-6 p-3.5 bg-rose-950/50 border border-rose-800/60 rounded-xl flex items-center gap-3 text-rose-200 text-xs">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Card Body */}
            <div className="p-6 md:p-8">
              {activeTab === 'quick' ? (
                /* TAB 1: 1-Click Persona Selector */
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-xs text-slate-400 pb-1">
                    <span className="font-medium text-slate-300">Hackathon Evaluation Personas</span>
                    <span>Click any role to log in instantly</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
                    {/* Role 1: Institution Admin */}
                    <div className="bg-slate-950/60 border border-slate-800 hover:border-blue-500/50 rounded-xl p-4 transition-all hover:shadow-lg hover:shadow-blue-900/10 flex flex-col justify-between group">
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
                            <Building2 className="w-4 h-4" />
                          </div>
                          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800/60">
                            Campus Admin
                          </span>
                        </div>
                        <h2 className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors">
                          Institution Admin
                        </h2>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                          Prof. Sunita Rao (Registrar, Apex Tech)
                        </p>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                          Batch intake upload, APAAR sync roster, and campus response.
                        </p>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-800/60 space-y-2">
                        <div className="text-[10px] font-mono text-slate-400 truncate">
                          admin@apex-tech.edu
                        </div>
                        <button
                          type="button"
                          disabled={loading}
                          onClick={() => handleQuickLogin('INSTITUTION_ADMIN')}
                          className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-sm active:scale-95 disabled:opacity-50"
                        >
                          <span>Sign In as Admin</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Role 2: Compliance Reviewer */}
                    <div className="bg-slate-950/60 border border-slate-800 hover:border-amber-500/50 rounded-xl p-4 transition-all hover:shadow-lg hover:shadow-amber-900/10 flex flex-col justify-between group">
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <div className="w-9 h-9 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center">
                            <ClipboardCheck className="w-4 h-4" />
                          </div>
                          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800/60">
                            Triage Desk
                          </span>
                        </div>
                        <h2 className="text-sm font-semibold text-white group-hover:text-amber-300 transition-colors">
                          Compliance Reviewer
                        </h2>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                          Er. Rajesh Pillai (Independent Evaluator)
                        </p>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                          Signal triage desk, evidence review, and accepting or overruling flags.
                        </p>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-800/60 space-y-2">
                        <div className="text-[10px] font-mono text-slate-400 truncate">
                          reviewer.desk@vidyasetu.local
                        </div>
                        <button
                          type="button"
                          disabled={loading}
                          onClick={() => handleQuickLogin('COMPLIANCE_REVIEWER')}
                          className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold bg-amber-600 hover:bg-amber-500 text-slate-950 font-bold transition-all shadow-sm active:scale-95 disabled:opacity-50"
                        >
                          <span>Sign In as Reviewer</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {/* Role 3: AICTE Regulator */}
                    <div className="bg-slate-950/60 border border-slate-800 hover:border-emerald-500/50 rounded-xl p-4 transition-all hover:shadow-lg hover:shadow-emerald-900/10 flex flex-col justify-between group">
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
                            <Scale className="w-4 h-4" />
                          </div>
                          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60">
                            Council Reviewer
                          </span>
                        </div>
                        <h2 className="text-sm font-semibold text-white group-hover:text-emerald-300 transition-colors">
                          AICTE Regulator
                        </h2>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                          Dr. V. K. Adhikari (AICTE Council Reviewer)
                        </p>
                        <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">
                          National oversight, rule configuration, policy analytics, and audit logs.
                        </p>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-800/60 space-y-2">
                        <div className="text-[10px] font-mono text-slate-400 truncate">
                          compliance.officer@aicte-gov.in
                        </div>
                        <button
                          type="button"
                          disabled={loading}
                          onClick={() => handleQuickLogin('REGULATOR_AICTE')}
                          className="w-full flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-sm active:scale-95 disabled:opacity-50"
                        >
                          <span>Sign In as Regulator</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                /* TAB 2: Manual Credentials Form */
                <form onSubmit={handleManualSubmit} className="max-w-md mx-auto space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">
                      Institutional Email
                    </label>
                    <div className="relative">
                      <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="e.g. admin@apex-tech.edu"
                        className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all font-mono"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-slate-300 mb-1.5">
                      Demo Password
                    </label>
                    <div className="relative">
                      <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter demo password"
                        className="w-full pl-9 pr-10 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all font-mono"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-2.5 px-4 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-md shadow-blue-600/30 active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
                  >
                    {loading ? (
                      <span className="inline-block w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                    ) : (
                      <>
                        <span>Sign In to VidyaSetu</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>

                  {/* Pre-configured Demo Credentials Cheatsheet */}
                  <div className="mt-6 pt-5 border-t border-slate-800/80">
                    <p className="text-[11px] font-semibold text-slate-400 mb-2">
                      Pre-Configured Demo Credentials (Click to pre-fill):
                    </p>
                    <div className="space-y-1.5 text-[11px] font-mono">
                      <button
                        type="button"
                        onClick={() => fillCredentials('admin@apex-tech.edu', 'DemoAdmin@2026')}
                        className="w-full text-left p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 text-slate-300 flex items-center justify-between transition-colors"
                      >
                        <span>admin@apex-tech.edu</span>
                        <span className="text-slate-500">DemoAdmin@2026</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => fillCredentials('reviewer.desk@vidyasetu.local', 'DemoReviewer@2026')}
                        className="w-full text-left p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 text-slate-300 flex items-center justify-between transition-colors"
                      >
                        <span>reviewer.desk@vidyasetu.local</span>
                        <span className="text-slate-500">DemoReviewer@2026</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => fillCredentials('compliance.officer@aicte-gov.in', 'DemoRegulator@2026')}
                        className="w-full text-left p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 text-slate-300 flex items-center justify-between transition-colors"
                      >
                        <span>compliance.officer@aicte-gov.in</span>
                        <span className="text-slate-500">DemoRegulator@2026</span>
                      </button>
                    </div>
                  </div>
                </form>
              )}
            </div>

            {/* Disclaimer & Transparency Footer */}
            <div className="px-6 md:px-8 py-4 bg-slate-950/60 border-t border-slate-800/80 flex items-start gap-2.5 text-[11px] text-slate-400">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-slate-300">Hackathon Prototype Isolation:</span>{' '}
                Session tokens are cryptographically signed using HMAC-SHA256 with 8-hour expiration. All student records, APAAR lookups, and institutional credentials in this environment are synthetic demonstrations for SIH 2026.
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-4 px-6 text-center text-xs text-slate-500 border-t border-slate-900 bg-slate-950">
        VidyaSetu Platform • SIH 2026 Problem Statement 26263 • Explainable Regulatory Intelligence
      </footer>
    </div>
  );
};
