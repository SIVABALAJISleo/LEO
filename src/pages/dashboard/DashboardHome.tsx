import { useDashboardData } from '@/hooks/useDashboardData';
import { useSystemHealthCheck } from '@/hooks/useSystemHealthCheck';
import { useRealtimeNotifications } from '@/hooks/useRealtimeNotifications';
import { SystemStatusCard } from '@/components/dashboard/SystemStatusCard';
import { PerformanceOverview } from '@/components/dashboard/PerformanceOverview';
import { ActiveJobsList } from '@/components/dashboard/ActiveJobsList';
import { RecentAlerts } from '@/components/dashboard/RecentAlerts';
import { ModuleCards } from '@/components/dashboard/ModuleCards';
import { PerformanceTrendsChart } from '@/components/dashboard/PerformanceTrendsChart';
import { GlobalStatusPill } from '@/components/dashboard/GlobalStatusPill';
import { JobQueueDisplay } from '@/components/dashboard/JobQueueDisplay';
import { AgentStatusBanner } from '@/components/dashboard/AgentStatusBanner';
import { GpuSavingsScoreCard } from '@/components/dashboard/GpuSavingsScoreCard';
import { UniversalPipelinePanel } from '@/components/dashboard/UniversalPipelinePanel';
import { LiveActivityFeed } from '@/components/dashboard/LiveActivityFeed';
import { QuickStats } from '@/components/dashboard/QuickStats';
import { ExecutionTransparencyPanel } from '@/components/dashboard/ExecutionTransparencyPanel';
import { RealityAuditMetrics } from '@/components/dashboard/RealityAuditMetrics';
import { ProductionAuditDashboard } from '@/components/dashboard/ProductionAuditDashboard';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

const DashboardHome = () => {
  const {
    loading,
    error,
    systemMetrics,
    activeJobs,
    alerts,
    moduleStatuses,
    moduleConfigs,
    performanceMetrics,
    refreshAll,
    resolveAlert,
  } = useDashboardData();

  // Enable continuous system health monitoring (runs every 5 minutes)
  useSystemHealthCheck(true, 300000);

  // Enable real-time toast notifications for job and alert events
  useRealtimeNotifications({
    enableJobNotifications: true,
    enableAlertNotifications: true,
    enableSystemNotifications: true,
  });

  // Calculate stats for QuickStats component
  const completedJobs = activeJobs.filter(j => j.status === 'completed').length;
  const runningJobs = activeJobs.filter(j => j.status === 'running' || j.status === 'queued').length;
  const failedJobs = activeJobs.filter(j => j.status === 'failed').length;

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-12 w-1/3 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Skeleton className="h-[400px] lg:col-span-2" />
          <Skeleton className="h-[400px]" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-destructive mb-4">{error}</p>
          <button
            onClick={refreshAll}
            className="text-primary hover:underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Agent Status Banner - PRODUCTION HONESTY */}
      <AgentStatusBanner />

      {/* Global Status */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">System Overview</h2>
        <GlobalStatusPill status={systemMetrics?.status || 'healthy'} />
      </div>

      {/* Quick Stats Summary */}
      <QuickStats
        totalJobs={activeJobs.length}
        completedJobs={completedJobs}
        activeJobs={runningJobs}
        failedJobs={failedJobs}
      />

      {/* Top Row: Reality Minimization + GPU Efficiency + Universal Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ExecutionTransparencyPanel />
        <GpuSavingsScoreCard />
        <UniversalPipelinePanel />
      </div>

      {/* Reality Audit Metrics - Full Width */}
      <RealityAuditMetrics />

      {/* Second Row: System Status & Performance Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SystemStatusCard
          metrics={systemMetrics}
          onRefresh={refreshAll}
        />
        <PerformanceOverview
          metrics={performanceMetrics}
          activeJobs={activeJobs}
        />
      </div>

      {/* Middle Row: Active Jobs, Job Queue & Recent Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <ActiveJobsList jobs={activeJobs} />
        <JobQueueDisplay />
        <RecentAlerts
          alerts={alerts}
          onResolve={resolveAlert}
        />
      </div>

      {/* Performance Trends + Live Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PerformanceTrendsChart metrics={performanceMetrics} />
        </div>
        <LiveActivityFeed />
      </div>

      {/* Module Cards Grid */}
      <ModuleCards
        statuses={moduleStatuses}
        configs={moduleConfigs}
      />

      {/* Production Audit Dashboard - Self-Protection & Autonomy */}
      <ProductionAuditDashboard />
    </div>
  );
};

export default DashboardHome;
