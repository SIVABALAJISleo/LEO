import { useState, useMemo } from 'react';
import { Briefcase, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { JobFilters } from '@/components/jobs/JobFilters';
import { JobCard } from '@/components/jobs/JobCard';
import { JobCreateForm } from '@/components/jobs/JobCreateForm';
import { JobDetailModal } from '@/components/jobs/JobDetailModal';
import { useJobsData, InferenceJob } from '@/hooks/useJobsData';

export default function JobsPage() {
  const { jobs, models, loading, error, refetch, createJob, cancelJob, retryJob } = useJobsData();

  // Filter & Sort state
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Detail modal state
  const [selectedJob, setSelectedJob] = useState<InferenceJob | null>(null);

  // Active tab
  const [activeTab, setActiveTab] = useState('all');

  // Filter and sort jobs
  const filteredJobs = useMemo(() => {
    let result = [...jobs];

    // Tab filter
    if (activeTab === 'active') {
      result = result.filter(j => ['queued', 'running'].includes(j.status));
    } else if (activeTab === 'completed') {
      result = result.filter(j => j.status === 'completed');
    } else if (activeTab === 'failed') {
      result = result.filter(j => ['failed', 'cancelled'].includes(j.status));
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(j =>
        j.id.toLowerCase().includes(query) ||
        j.model?.name?.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      result = result.filter(j => j.status === statusFilter);
    }

    // Priority filter
    if (priorityFilter !== 'all') {
      result = result.filter(j => {
        if (priorityFilter === 'high') return j.priority <= 3;
        if (priorityFilter === 'normal') return j.priority >= 4 && j.priority <= 6;
        if (priorityFilter === 'low') return j.priority >= 7;
        return true;
      });
    }

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'created_at':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        case 'priority':
          comparison = a.priority - b.priority;
          break;
        case 'progress':
          comparison = (a.progress || 0) - (b.progress || 0);
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [jobs, activeTab, searchQuery, statusFilter, priorityFilter, sortBy, sortOrder]);

  // Job counts by status
  const jobCounts = useMemo(() => ({
    all: jobs.length,
    active: jobs.filter(j => ['queued', 'running'].includes(j.status)).length,
    completed: jobs.filter(j => j.status === 'completed').length,
    failed: jobs.filter(j => ['failed', 'cancelled'].includes(j.status)).length
  }), [jobs]);

  const handleCancelJob = async () => {
    if (selectedJob) {
      await cancelJob(selectedJob.id);
      setSelectedJob(null);
    }
  };

  const handleRetryJob = async () => {
    if (selectedJob) {
      await retryJob(selectedJob.id);
      setSelectedJob(null);
    }
  };

  if (error) {
    return (
      <div className="p-6 text-center">
        <p className="text-destructive mb-4">{error}</p>
        <Button onClick={refetch}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary/10 rounded-lg">
            <Briefcase className="h-6 w-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">Inference Jobs</h1>
            <p className="text-sm text-muted-foreground">
              Manage and monitor your GPU inference jobs
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={refetch} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <JobCreateForm models={models} onSubmit={createJob} />
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-muted/50">
          <TabsTrigger value="all">
            All Jobs ({jobCounts.all})
          </TabsTrigger>
          <TabsTrigger value="active">
            Active ({jobCounts.active})
          </TabsTrigger>
          <TabsTrigger value="completed">
            Completed ({jobCounts.completed})
          </TabsTrigger>
          <TabsTrigger value="failed">
            Failed ({jobCounts.failed})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4 space-y-4">
          {/* Filters */}
          <JobFilters
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            statusFilter={statusFilter}
            onStatusFilterChange={setStatusFilter}
            priorityFilter={priorityFilter}
            onPriorityFilterChange={setPriorityFilter}
            sortBy={sortBy}
            onSortByChange={setSortBy}
            sortOrder={sortOrder}
            onSortOrderToggle={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
          />

          {/* Job List */}
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-32 rounded-lg" />
              ))}
            </div>
          ) : filteredJobs.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No jobs found matching your criteria.</p>
              <p className="text-sm mt-2">Create a new job to get started.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredJobs.map(job => (
                <JobCard
                  key={job.id}
                  job={job}
                  onViewDetails={() => setSelectedJob(job)}
                  onCancel={() => cancelJob(job.id)}
                  onRetry={() => retryJob(job.id)}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Job Detail Modal */}
      <JobDetailModal
        job={selectedJob}
        open={!!selectedJob}
        onOpenChange={(open) => !open && setSelectedJob(null)}
        onCancel={handleCancelJob}
        onRetry={handleRetryJob}
      />
    </div>
  );
}
