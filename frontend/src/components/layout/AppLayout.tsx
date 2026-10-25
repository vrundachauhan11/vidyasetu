import React from 'react';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { RoleType, UserProfile } from '../../types';

interface AppLayoutProps {
  children: React.ReactNode;
  currentTab: string;
  onSelectTab: (tab: string) => void;
  currentUser: UserProfile | null;
  onSwitchRole: (role: RoleType) => void;
  onLogout: () => void;
  isBackendHealthy: boolean;
  reviewCount?: number;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  children,
  currentTab,
  onSelectTab,
  currentUser,
  onSwitchRole,
  onLogout,
  isBackendHealthy,
  reviewCount = 0,
}) => {
  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
      <Sidebar
        currentTab={currentTab}
        onSelectTab={onSelectTab}
        currentUser={currentUser}
        onLogout={onLogout}
        reviewCount={reviewCount}
      />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar
          currentUser={currentUser}
          onSwitchRole={onSwitchRole}
          onLogout={onLogout}
          isBackendHealthy={isBackendHealthy}
        />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-50/70">
          <div className="max-w-7xl mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
