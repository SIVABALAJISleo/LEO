import { Routes, Route, Navigate } from 'react-router-dom';
import { SidebarProvider } from '@/components/ui/sidebar';
import { DashboardSidebar } from '@/components/dashboard/DashboardSidebar';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { useBackendInitialization } from '@/hooks/useBackendInitialization';
import DashboardHome from '@/pages/dashboard/DashboardHome';
import ModulesPage from '@/pages/dashboard/ModulesPage';
import JobsPage from '@/pages/dashboard/JobsPage';
import MonitoringPage from '@/pages/dashboard/MonitoringPage';
import InferencePage from '@/pages/dashboard/InferencePage';
import ResultsPage from '@/pages/dashboard/ResultsPage';
import SettingsPage from '@/pages/dashboard/SettingsPage';
import OrchestrationExplorer from '@/pages/OrchestrationExplorer';
import SystemDashboard from '@/pages/SystemDashboard';
import GpuBypassDemo from '@/pages/GpuBypassDemo';
import VisionPage from '@/pages/dashboard/VisionPage';
import JepaPage from '@/pages/dashboard/JepaPage';
import SotaPage from '@/pages/dashboard/SotaPage';

import SecurityPage from '@/pages/advanced/SecurityPage';
import CostAnalyticsPage from '@/pages/advanced/CostAnalyticsPage';
import DisasterRecoveryPage from '@/pages/advanced/DisasterRecoveryPage';

const Dashboard = () => {
  // Initialize backend on dashboard mount - seeds data and starts automation
  const { initialized, loading, health } = useBackendInitialization();
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <DashboardSidebar />
        <div className="flex-1 flex flex-col min-h-screen">
          <DashboardHeader />
          <main className="flex-1 overflow-auto">
            <Routes>
              {/* Core Dashboard Routes */}
              <Route path="home" element={<DashboardHome />} />
              <Route path="jobs" element={<JobsPage />} />
              <Route path="models" element={<DashboardHome />} />
              <Route path="modules" element={<ModulesPage />} />
              <Route path="monitoring" element={<MonitoringPage />} />
              <Route path="inference" element={<InferencePage />} />
              <Route path="results" element={<ResultsPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="analytics" element={<MonitoringPage />} />
              <Route path="vision" element={<VisionPage />} />
              <Route path="jepa" element={<JepaPage />} />
              <Route path="sota" element={<SotaPage />} />

              {/* Production Functional Routes */}
              <Route path="orchestration" element={<OrchestrationExplorer />} />
              <Route path="telemetry" element={<SystemDashboard />} />
              <Route path="gpu-bypass" element={<GpuBypassDemo />} />

              {/* Advanced Security & Disaster Recovery */}
              <Route path="advanced/security" element={<SecurityPage />} />
              <Route path="advanced/cost-analytics" element={<CostAnalyticsPage />} />
              <Route path="advanced/disaster-recovery" element={<DisasterRecoveryPage />} />

              {/* Catch-all */}
              <Route path="*" element={<Navigate to="home" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default Dashboard;
