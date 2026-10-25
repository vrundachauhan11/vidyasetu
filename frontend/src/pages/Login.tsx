import React, { useState } from 'react';
import {
  ShieldCheck,
  Eye,
  EyeOff,
  Lock,
  Mail,
  ArrowRight,
  AlertTriangle,
  ChevronDown,
  Building2,
  ClipboardCheck,
  Scale,
  Sparkles,
  Info,
} from 'lucide-react';
import { api } from '../services/api';
import { RoleType, UserProfile } from '../types';

interface LoginProps {
  onLoginSuccess: (user: UserProfile) => void;
  targetNotice?: string;
}

const DEMO_PERSONAS = [
  {
    role: 'INSTITUTION_ADMIN' as RoleType,
    title: 'Institution Admin',
    shortRole: 'Admin',
    name: 'Prof. Sunita Rao (Apex Tech)',
    email: 'admin@apex-tech.edu',
    password: 'DemoAdmin@2026',
    icon: Building2,
  },
  {
    role: 'COMPLIANCE_REVIEWER' as RoleType,
    title: 'Compliance Reviewer',
    shortRole: 'Reviewer',
    name: 'Er. Rajesh Pillai (Review Desk)',
    email: 'reviewer.desk@vidyasetu.local',
    password: 'DemoReviewer@2026',
    icon: ClipboardCheck,
  },
  {
    role: 'REGULATOR_AICTE' as RoleType,
    title: 'AICTE Regulator',
    shortRole: 'Regulator',
    name: 'Dr. V. K. Adhikari (Council Reviewer)',
    email: 'compliance.officer@aicte-gov.in',
    password: 'DemoRegulator@2026',
    icon: Scale,
  },
];

export const Login: React.FC<LoginProps> = ({ onLoginSuccess, targetNotice }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [showDemoAccounts, setShowDemoAccounts] = useState(false);

  const handleManualSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setErrorMsg('Please enter both your email address and password.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    try {
      const resp = await api.login({ email, password });
      onLoginSuccess(resp.user);
    } catch (err: any) {
      setErrorMsg(err.message || 'Invalid demo credentials. Please verify your email and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (role: RoleType) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const resp = await api.login({ role });
      onLoginSuccess(resp.user);
    } catch (err: any) {
      setErrorMsg(err.message || 'Sign-in failed. Please verify the backend service is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDemoAccount = (demoEmail: string, demoPassword: string) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setErrorMsg(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-4 sm:p-6 font-sans text-slate-800 selection:bg-blue-600 selection:text-white">
      {/* Brand Header */}
      <div className="flex flex-col items-center mb-6 text-center">
        <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-600/20 mb-3">
          <ShieldCheck className="w-5 h-5" />
        </div>
        <div className="flex items-center gap-2">
          <span className="font-bold text-slate-900 text-xl tracking-tight">VidyaSetu</span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
            RegTech
          </span>
        </div>
        <p className="text-xs text-slate-500 mt-0.5">Student Data & Verification Platform</p>
      </div>

      {/* Centered Sign-In Card */}
      <div className="w-full max-w-md bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-8 space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Welcome back</h1>
          <p className="text-xs text-slate-500 mt-1">
            Sign in to your institutional account to continue.
          </p>
        </div>

        {/* Target Redirection Notice */}
        {targetNotice && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-2.5 text-xs text-blue-900">
            <Info className="w-4 h-4 text-blue-600 shrink-0" />
            <span className="leading-snug">{targetNotice}</span>
          </div>
        )}

        {/* Error Alert */}
        {errorMsg && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-2.5 text-xs text-rose-800">
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
            <span className="leading-snug">{errorMsg}</span>
          </div>
        )}

        {/* Standard Credentials Form */}
        <form onSubmit={handleManualSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-xs font-medium text-slate-700 mb-1.5">
              Email address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@institution.edu"
                className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all font-mono"
                required
              />
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="password" className="block text-xs font-medium text-slate-700">
                Password
              </label>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-9 pr-10 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all font-mono"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Prominent Sign In Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-xl text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white transition-all shadow-xs flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            {loading ? (
              <span className="inline-block w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <span>Sign in</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-slate-200" />
          </div>
          <div className="relative flex justify-center text-[10px] uppercase">
            <span className="bg-white px-2 text-slate-400 font-medium">OR</span>
          </div>
        </div>

        {/* Google OAuth (Unconfigured / Disabled Placeholder) */}
        <div>
          <button
            type="button"
            disabled
            title="Google OAuth integration is not configured in this prototype environment"
            className="w-full py-2 px-4 rounded-xl text-xs font-medium bg-slate-50 text-slate-400 border border-slate-200 flex items-center justify-center gap-2.5 cursor-not-allowed transition-all"
          >
            {/* Google Multicolor SVG */}
            <svg className="w-4 h-4 opacity-50" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>Continue with Google</span>
            <span className="text-[10px] text-slate-400 font-mono">(Pending Setup)</span>
          </button>
        </div>

        {/* Compact, Unobtrusive Demo Account Accessor */}
        <div className="pt-2">
          <button
            type="button"
            onClick={() => setShowDemoAccounts(!showDemoAccounts)}
            className="w-full flex items-center justify-center gap-1.5 text-xs text-blue-600 hover:text-blue-700 font-medium py-1.5 transition-colors"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Use a demo account</span>
            <ChevronDown
              className={`w-3.5 h-3.5 transition-transform duration-200 ${
                showDemoAccounts ? 'rotate-180' : ''
              }`}
            />
          </button>

          {/* Collapsible Demo Personas Menu */}
          {showDemoAccounts && (
            <div className="mt-3 p-3 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2 text-xs">
              <div className="text-[11px] font-semibold text-slate-600 pb-1 border-b border-slate-200/60 flex items-center justify-between">
                <span>Select a Demo Role:</span>
                <span className="text-[10px] text-slate-400 font-normal">Click to fill or sign in</span>
              </div>

              <div className="space-y-1.5">
                {DEMO_PERSONAS.map((persona) => {
                  const Icon = persona.icon;
                  return (
                    <div
                      key={persona.role}
                      className="p-2 bg-white rounded-lg border border-slate-200/70 hover:border-blue-400 flex items-center justify-between gap-2 transition-all group"
                    >
                      <button
                        type="button"
                        onClick={() => handleSelectDemoAccount(persona.email, persona.password)}
                        className="flex items-center gap-2 min-w-0 text-left flex-1"
                        title="Click to fill email and password"
                      >
                        <div className="w-7 h-7 rounded-md bg-slate-100 group-hover:bg-blue-50 text-slate-600 group-hover:text-blue-600 flex items-center justify-center shrink-0 transition-colors">
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <div className="min-w-0">
                          <span className="block font-semibold text-slate-800 text-[11px] truncate">
                            {persona.title}
                          </span>
                          <span className="block text-[10px] text-slate-400 font-mono truncate">
                            {persona.email}
                          </span>
                        </div>
                      </button>

                      <button
                        type="button"
                        disabled={loading}
                        onClick={() => handleQuickLogin(persona.role)}
                        className="px-2.5 py-1 text-[11px] font-semibold rounded-md bg-slate-100 hover:bg-blue-600 hover:text-white text-slate-700 transition-colors shrink-0 disabled:opacity-50"
                      >
                        Sign in as {persona.shortRole}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Subtle Footer Prototype Notice */}
      <div className="mt-6 text-center text-xs text-slate-400 space-y-1">
        <p>SIH 2026 Prototype · Demo accounts available</p>
        <p className="text-[11px] text-slate-400/80">
          Deterministic simulation for Problem Statement 26263
        </p>
      </div>
    </div>
  );
};
