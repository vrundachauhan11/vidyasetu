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
import { RoleType, UserProfile, DashboardData } from './types';
import { api } from './services/api';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);

  const loadInitialData = async () => {
    try {
      const health = await api.getHealth();
      setIsBackendHealthy(health.status === 'healthy' || health.database?.connected);
    } catch {
      setIsBackendHealthy(false);
    }

    try {
      const user = await api.getCurrentUser();
      setCurrentUser(user);
    } catch (err) {
      console.warn('Failed to fetch user:', err);
    }

    try {
      const data = await api.getDashboardOverview();
      setDashboardData(data);
    } catch (err) {
      console.warn('Failed to fetch dashboard overview:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
    const interval = setInterval(loadInitialData, 30000); // 30s background sync
    return () => clearInterval(interval);
  }, []);

  const handleSwitchRole = async (role: RoleType) => {
    try {
      const updatedUser = await api.switchRole(role);
      setCurrentUser(updatedUser);
    } catch (err) {
      console.error('Failed to switch role:', err);
    }
  };

  const renderContent = () => {
    switch (currentTab) {
      case 'overview':
        return <Overview data={dashboardData} loading={loading} onNavigate={setCurrentTab} />;
      case 'institutions':
        return <Institutions />;
      case 'students':
        return <StudentRecords />;
      case 'intake':
        return <DataIntake />;
      case 'apaar':
        return <ApaarValidation />;
      case 'integrity':
        return <IntakeIntegrity onNavigateToReview={() => setCurrentTab('review')} />;
      case 'review':
        return <EvidenceReview />;
      case 'verification':
        return <Verification />;
      case 'reports':
        return <Reports />;
      case 'audit':
        return <AuditLog />;
      case 'settings':
        return <Settings />;
      default:
        return <Overview data={dashboardData} loading={loading} onNavigate={setCurrentTab} />;
    }
  };

  return (
    <AppLayout
      currentTab={currentTab}
      onSelectTab={setCurrentTab}
      currentUser={currentUser}
      onSwitchRole={handleSwitchRole}
      isBackendHealthy={isBackendHealthy}
      reviewCount={dashboardData?.metrics?.active_signals || 0}
    >
      {renderContent()}
    </AppLayout>
  );
}

export default App;
