import React, { useEffect, useState } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { Overview } from './pages/Overview';
import { Institutions } from './pages/Institutions';
import { StudentRecords } from './pages/StudentRecords';
import { DataIntake } from './pages/DataIntake';
import { ApaarValidation } from './pages/ApaarValidation';
import { IntakeIntegrity } from './pages/IntakeIntegrity';
import { EvidenceReview } from './pages/EvidenceReview';
import { Verification } from './pages/Verification';
import { Reports } from './pages/Reports';
import { AuditLog } from './pages/AuditLog';
import { Settings } from './pages/Settings';
import { Login } from './pages/Login';
import { RoleType, UserProfile, DashboardData } from './types';
import { api, getStoredToken } from './services/api';

const VALID_TABS = [
  'overview',
  'institutions',
  'students',
  'intake',
  'apaar',
  'integrity',
  'review',
  'verification',
  'reports',
  'audit',
  'settings',
  'login',
];

export function App() {
  const getInitialTab = () => {
    if (typeof window !== 'undefined') {
      const path = window.location.pathname.replace('/', '').trim();
      const hash = window.location.hash.replace('#', '').trim();
      if (path === 'login' || hash === 'login') return 'login';
      if (VALID_TABS.includes(hash)) return hash;
    }
    return 'overview';
  };

  const [currentTab, setCurrentTab] = useState<string>(getInitialTab);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [authLoading, setAuthLoading] = useState<boolean>(true);
  const [dataLoading, setDataLoading] = useState<boolean>(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);
  const [redirectNotice, setRedirectNotice] = useState<string | null>(null);

  const handleSelectTab = (tab: string) => {
    if (typeof window !== 'undefined') {
      window.location.hash = tab;
    }
    setCurrentTab(tab);
  };

  const loadDashboardData = async () => {
    setDataLoading(true);
    try {
      const data = await api.getDashboardOverview();
      setDashboardData(data);
    } catch (err) {
      console.warn('Failed to fetch dashboard overview:', err);
    } finally {
      setDataLoading(false);
    }
  };

  const checkAuthAndInit = async () => {
    // 1. Check system health probe
    try {
      const health = await api.getHealth();
      setIsBackendHealthy(health.status === 'healthy' || health.database?.connected);
    } catch {
      setIsBackendHealthy(false);
    }

    // 2. Verify active session token
    const token = getStoredToken();
    if (!token) {
      setCurrentUser(null);
      setAuthLoading(false);
      const currentHash = window.location.hash.replace('#', '').trim();
      if (currentHash && currentHash !== 'login') {
        setRedirectNotice(`Authentication required to access '${currentHash}' workspace.`);
      }
      handleSelectTab('login');
      return;
    }

    try {
      const user = await api.getCurrentUser();
      setCurrentUser(user);
      setRedirectNotice(null);
      await loadDashboardData();
    } catch (err) {
      console.warn('Stored token is invalid or expired:', err);
      api.clearToken();
      setCurrentUser(null);
      setRedirectNotice('Your demo session has expired. Please sign in again.');
      handleSelectTab('login');
    } finally {
      setAuthLoading(false);
    }
  };

  useEffect(() => {
    checkAuthAndInit();

    const interval = setInterval(() => {
      if (getStoredToken()) {
        loadDashboardData();
      }
    }, 30000); // 30s background sync

    const onHashChange = () => {
      const h = window.location.hash.replace('#', '').trim();
      if (VALID_TABS.includes(h)) {
        setCurrentTab(h);
      }
    };
    window.addEventListener('hashchange', onHashChange);

    return () => {
      clearInterval(interval);
      window.removeEventListener('hashchange', onHashChange);
    };
  }, []);

  const handleLoginSuccess = async (user: UserProfile) => {
    setCurrentUser(user);
    setRedirectNotice(null);

    // Redirect to relevant operational tab based on persona
    let nextTab = 'overview';
    if (user.role === 'INSTITUTION_ADMIN') {
      nextTab = 'intake';
    } else if (user.role === 'COMPLIANCE_REVIEWER') {
      nextTab = 'review';
    }
    handleSelectTab(nextTab);
    await loadDashboardData();
  };

  const handleLogout = async () => {
    await api.logout();
    setCurrentUser(null);
    setDashboardData(null);
    setRedirectNotice('You have successfully signed out of the VidyaSetu prototype.');
    handleSelectTab('login');
  };

  const handleSwitchRole = async (role: RoleType) => {
    try {
      const updatedUser = await api.switchRole(role);
      setCurrentUser(updatedUser);
      await loadDashboardData();
    } catch (err) {
      console.error('Failed to switch role:', err);
    }
  };

  // Loading Splash Screen while checking initial token state
  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center font-sans text-slate-300">
        <div className="w-12 h-12 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 mb-4 animate-pulse">
          <span className="font-bold text-lg">VS</span>
        </div>
        <p className="text-xs font-semibold tracking-wider text-slate-200">INITIALIZING VIDYASETU</p>
        <p className="text-[11px] text-slate-500 mt-1">Verifying regulatory session token...</p>
      </div>
    );
  }

  // Unauthenticated users land on dedicated /login route
  if (!currentUser || currentTab === 'login') {
    return (
      <Login
        onLoginSuccess={handleLoginSuccess}
        targetNotice={redirectNotice || undefined}
      />
    );
  }

  const renderContent = () => {
    switch (currentTab) {
      case 'overview':
        return <Overview data={dashboardData} loading={dataLoading} onNavigate={handleSelectTab} />;
      case 'institutions':
        return <Institutions />;
      case 'students':
        return <StudentRecords />;
      case 'intake':
        return <DataIntake currentUser={currentUser} />;
      case 'apaar':
        return <ApaarValidation />;
      case 'integrity':
        return <IntakeIntegrity onNavigateToReview={() => handleSelectTab('review')} />;
      case 'review':
        return <EvidenceReview currentUser={currentUser} />;
      case 'verification':
        return <Verification />;
      case 'reports':
        return <Reports />;
      case 'audit':
        return <AuditLog />;
      case 'settings':
        return <Settings currentUser={currentUser} onLogout={handleLogout} />;
      default:
        return <Overview data={dashboardData} loading={dataLoading} onNavigate={handleSelectTab} />;
    }
  };

  return (
    <AppLayout
      currentTab={currentTab}
      onSelectTab={handleSelectTab}
      currentUser={currentUser}
      onSwitchRole={handleSwitchRole}
      onLogout={handleLogout}
      isBackendHealthy={isBackendHealthy}
      reviewCount={dashboardData?.metrics?.active_signals || 0}
    >
      {renderContent()}
    </AppLayout>
  );
}

export default App;
