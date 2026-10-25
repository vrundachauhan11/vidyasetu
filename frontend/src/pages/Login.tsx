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
  AlertTriangle,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { api } from '../services/api';
import { RoleType, UserProfile, DemoRoleInfo } from '../types';

interface LoginProps {
  onLoginSuccess: (user: UserProfile) => void;
  targetNotice?: string;
}

const PIPELINE_STAGES = [
  { step: '01', name: 'Institution', desc: 'Sanctioned intake capacity & approval profile' },
  { step: '02', name: 'Data Intake', desc: 'Schema checks, CSV intake & duplicate detection' },
  { step: '03', name: 'APAAR Validation', desc: 'Simulated National Academic Depository sync' },
  { step: '04', name: 'Integrity Checks', desc: 'Deterministic statutory rule evaluation' },
  { step: '05', name: 'Repository', desc: 'Version-controlled enrolment ledger & audit log' },
  { step: '06', name: 'Review & Analytics', desc: 'Triage desk, evidence review & trend analytics' },
  { step: '07', name: 'Verification', desc: 'Verifiable credentials & SHA-256 tamper checks' },
];

export const Login: React.FC<LoginProps> = ({ onLoginSuccess, targetNotice }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'quick' | 'manual'>('quick');
  const [demoRoles, setDemoRoles] = useState<DemoRoleInfo[]>([]);

  useEffect(() => {
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
      setErrorMsg(err.message || 'Invalid demo credentials. Please verify your email or password.');
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

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      {/* Responsive Split Screen Container */}
      <div className="flex-1 flex flex-col lg:flex-row w-full min-h-screen">
        
        {/* ========================================================================= */}
        {/* LEFT PANEL: Branding, Value Proposition & 7-Stage Workflow Illustration */}
        {/* ========================================================================= */}
        <aside className="lg:w-5/12 xl:w-5/12 bg-white border-b lg:border-b-0 lg:border-r border-slate-200/90 p-6 sm:p-8 lg:p-12 flex flex-col justify-between">
          <div className="space-y-8">
            {/* Logo Mark & Header */}
            <div>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-600/20">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900 tracking-tight text-xl">VidyaSetu</span>
                    <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                      RegTech
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 font-medium">Explainable Enrolment Integrity</p>
                </div>
              </div>

              {/* Subtitle & Mission Statement */}
              <div className="mt-6 space-y-2">
                <h2 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
                  Explainable Enrolment Integrity & Regulatory Intelligence
                </h2>
                <p className="text-xs text-slate-600 leading-relaxed">
                  VidyaSetu supports AICTE-approved institutions with deterministic enrolment validation, evidence-led compliance review, and real-time regulatory oversight.
                </p>
              </div>
            </div>

            {/* 7-Stage Workflow Lifecycle */}
            <div className="bg-slate-50/70 rounded-xl p-4 sm:p-5 border border-slate-200/80 space-y-3.5">
              <div className="flex items-center justify-between pb-2.5 border-b border-slate-200/60">
                <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                  Enrolment Integrity Pipeline
                </span>
                <span className="text-[10px] text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200 font-medium">
                  7-Stage Workflow
                </span>
              </div>

              <div className="relative pl-6 space-y-3 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
                {PIPELINE_STAGES.map((st, idx) => (
                  <div key={st.step} className="relative flex items-baseline justify-between text-xs gap-3">
                    <span className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-blue-600 border-2 border-white ring-2 ring-blue-100 shrink-0" />
                    <div className="min-w-0">
                      <span className="font-semibold text-slate-800 text-xs">
                        {idx + 1}. {st.name}
                      </span>
                      <p className="text-[11px] text-slate-500 truncate leading-tight">
                        {st.desc}
                      </p>
                    </div>
                    <span className="font-mono text-[10px] text-slate-400 shrink-0">
                      Stage {st.step}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Prototype Disclosure Footer Tag */}
          <div className="mt-8 pt-6 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium text-[11px] border border-slate-200/60">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-500" />
              SIH 2026 Prototype · Synthetic Demo Data
            </span>
            <span className="text-[11px] font-mono text-slate-400">PS 26263</span>
          </div>
        </aside>

        {/* ========================================================================= */}
        {/* RIGHT PANEL: Sign-In Desk with Segmented Control & Clean Role Cards       */}
        {/* ========================================================================= */}
        <main className="lg:w-7/12 xl:w-7/12 bg-white flex flex-col justify-center px-6 py-10 sm:px-10 lg:px-16 overflow-y-auto">
          <div className="max-w-lg w-full mx-auto space-y-6">
            
            {/* Section Header */}
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
                Welcome to VidyaSetu
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-1.5">
                Choose a demonstration role to continue.
              </p>
            </div>

            {/* Segmented Control Switcher */}
            <div className="flex p-1 bg-slate-100 rounded-lg border border-slate-200 text-xs font-medium">
              <button
                type="button"
                onClick={() => { setActiveTab('quick'); setErrorMsg(null); }}
                className={`flex-1 py-2 rounded-md transition-all text-center ${
                  activeTab === 'quick'
                    ? 'bg-white text-slate-900 font-semibold shadow-xs border border-slate-200/60'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Quick Demo Login
              </button>
              <button
                type="button"
                onClick={() => { setActiveTab('manual'); setErrorMsg(null); }}
                className={`flex-1 py-2 rounded-md transition-all text-center ${
                  activeTab === 'manual'
                    ? 'bg-white text-slate-900 font-semibold shadow-xs border border-slate-200/60'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Email & Password
              </button>
            </div>

            {/* Target Redirect Notice */}
            {targetNotice && (
              <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-3 text-xs text-blue-900">
                <Info className="w-4 h-4 text-blue-600 shrink-0" />
                <span className="leading-snug">{targetNotice}</span>
              </div>
            )}

            {/* Error Message Alert */}
            {errorMsg && (
              <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-3 text-xs text-rose-800">
                <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                <span className="leading-snug">{errorMsg}</span>
              </div>
            )}

            {/* =================================================================== */}
            {/* TAB 1: Three Clean Role Options                                    */}
            {/* =================================================================== */}
            {activeTab === 'quick' && (
              <div className="space-y-3 pt-1">
                {/* 1. Institution Admin */}
                <div className="p-4 rounded-xl border border-slate-200 hover:border-blue-400 bg-white hover:bg-slate-50/50 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-2xs">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center shrink-0 mt-0.5">
                      <Building2 className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-semibold text-slate-900">Institution Admin</h3>
                        <span className="text-[10px] text-slate-500 truncate hidden sm:inline">
                          Prof. Sunita Rao (Apex Tech)
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5 leading-snug">
                        Upload rosters and manage institutional intake.
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => handleQuickLogin('INSTITUTION_ADMIN')}
                    className="w-full sm:w-auto px-4 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-700 text-white shrink-0 transition-all shadow-xs flex items-center justify-center gap-1.5 disabled:opacity-50 active:scale-95"
                  >
                    <span>Sign In as Admin</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* 2. Compliance Reviewer */}
                <div className="p-4 rounded-xl border border-slate-200 hover:border-teal-400 bg-white hover:bg-slate-50/50 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-2xs">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className="w-9 h-9 rounded-lg bg-teal-50 text-teal-700 border border-teal-100 flex items-center justify-center shrink-0 mt-0.5">
                      <ClipboardCheck className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-semibold text-slate-900">Compliance Reviewer</h3>
                        <span className="text-[10px] text-slate-500 truncate hidden sm:inline">
                          Er. Rajesh Pillai (Evaluator)
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5 leading-snug">
                        Investigate findings and record review decisions.
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => handleQuickLogin('COMPLIANCE_REVIEWER')}
                    className="w-full sm:w-auto px-4 py-2 text-xs font-semibold rounded-lg bg-teal-700 hover:bg-teal-800 text-white shrink-0 transition-all shadow-xs flex items-center justify-center gap-1.5 disabled:opacity-50 active:scale-95"
                  >
                    <span>Sign In as Reviewer</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* 3. AICTE Regulator */}
                <div className="p-4 rounded-xl border border-slate-200 hover:border-slate-400 bg-white hover:bg-slate-50/50 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-2xs">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className="w-9 h-9 rounded-lg bg-slate-100 text-slate-700 border border-slate-200 flex items-center justify-center shrink-0 mt-0.5">
                      <Scale className="w-4 h-4" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-semibold text-slate-900">AICTE Regulator</h3>
                        <span className="text-[10px] text-slate-500 truncate hidden sm:inline">
                          Dr. V. K. Adhikari (Council Reviewer)
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5 leading-snug">
                        Review regulatory indicators and configured rules.
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => handleQuickLogin('REGULATOR_AICTE')}
                    className="w-full sm:w-auto px-4 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-900 text-white shrink-0 transition-all shadow-xs flex items-center justify-center gap-1.5 disabled:opacity-50 active:scale-95"
                  >
                    <span>Sign In as Regulator</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}

            {/* =================================================================== */}
            {/* TAB 2: Manual Credentials Form                                     */}
            {/* =================================================================== */}
            {activeTab === 'manual' && (
              <form onSubmit={handleManualSubmit} className="space-y-4 pt-1">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1.5">
                    Institutional Email
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="e.g. admin@apex-tech.edu"
                      className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all font-mono"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1.5">
                    Demo Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter demo password"
                      className="w-full pl-9 pr-10 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all font-mono"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 px-4 rounded-lg text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-xs flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50"
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

                {/* Pre-configured Demo Accounts Helper */}
                <div className="pt-4 border-t border-slate-100 space-y-2">
                  <span className="text-[11px] font-semibold text-slate-600 block">
                    Credential Hints for Evaluation (Click to pre-fill):
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => fillCredentials('admin@apex-tech.edu', 'DemoAdmin@2026')}
                      className="p-2 text-left bg-slate-50 hover:bg-blue-50/60 border border-slate-200/80 rounded-lg transition-colors group"
                    >
                      <span className="block text-[11px] font-semibold text-slate-800 group-hover:text-blue-700">Admin</span>
                      <span className="block text-[10px] text-slate-500 font-mono truncate">admin@apex-tech.edu</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => fillCredentials('reviewer.desk@vidyasetu.local', 'DemoReviewer@2026')}
                      className="p-2 text-left bg-slate-50 hover:bg-teal-50/60 border border-slate-200/80 rounded-lg transition-colors group"
                    >
                      <span className="block text-[11px] font-semibold text-slate-800 group-hover:text-teal-700">Reviewer</span>
                      <span className="block text-[10px] text-slate-500 font-mono truncate">reviewer.desk@...</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => fillCredentials('compliance.officer@aicte-gov.in', 'DemoRegulator@2026')}
                      className="p-2 text-left bg-slate-50 hover:bg-slate-100 border border-slate-200/80 rounded-lg transition-colors group"
                    >
                      <span className="block text-[11px] font-semibold text-slate-800 group-hover:text-slate-900">Regulator</span>
                      <span className="block text-[10px] text-slate-500 font-mono truncate">compliance.officer@...</span>
                    </button>
                  </div>
                </div>
              </form>
            )}

            {/* =================================================================== */}
            {/* Compact Security & Prototype Disclosure                             */}
            {/* =================================================================== */}
            <div className="pt-4 border-t border-slate-100 flex items-start gap-2.5 text-[11px] text-slate-500">
              <ShieldCheck className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
              <p className="leading-relaxed">
                <strong>Hackathon Prototype Notice:</strong> Uses synthetic demo identities and simulated external integrations. No real student PII or production credentials stored.
              </p>
            </div>

          </div>
        </main>

      </div>
    </div>
  );
};
