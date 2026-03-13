import { useQuery } from '@tanstack/react-query';
import { api } from '@/hooks/useBackendInitialization';
import { Badge } from '@/components/ui/badge';
import { Loader2, Server, Clock, Image, FileText, Cpu } from 'lucide-react';

interface JobRecord {
  job_id: string;
  job_type: string;
  status: string;
  created_at: number;
}

const JobsPage = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['saas_job_history'],
    queryFn: async () => {
      const res = await api.get('/api/v1/jobs/user/history');
      return res.data.jobs as JobRecord[];
    },
    refetchInterval: 5000, // Poll queue history
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500/10 text-green-500 hover:bg-green-500/20';
      case 'running': return 'bg-brand-500/10 text-brand-500 hover:bg-brand-500/20';
      case 'queued': return 'bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20';
      case 'failed': return 'bg-red-500/10 text-red-500 hover:bg-red-500/20';
      default: return 'bg-gray-500/10 text-gray-500';
    }
  };

  const getJobIcon = (type: string) => {
    switch (type) {
      case 'llm': return <FileText className="h-4 w-4 text-brand-400" />;
      case 'vision_detect': return <Image className="h-4 w-4 text-blue-400" />;
      case 'vision_caption': return <Image className="h-4 w-4 text-emerald-400" />;
      case 'jepa_compare': return <Cpu className="h-4 w-4 text-purple-400" />;
      default: return <Server className="h-4 w-4 text-gray-400" />;
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Distributed Jobs Queue</h1>
        <p className="text-muted-foreground">
          Real-time view of your asynchronous AI inferences executing across the Celery cluster.
        </p>
      </div>

      <div className="rounded-md border bg-card text-card-foreground shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center p-12">
            <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
            <span className="ml-3 text-muted-foreground">Querying DB...</span>
          </div>
        ) : error ? (
          <div className="p-12 text-center text-red-500">Failed to load jobs queue. Ensure SaaS API is running.</div>
        ) : !data || data.length === 0 ? (
          <div className="p-12 text-center text-muted-foreground">No distributed jobs found. Create one from the Dashboard.</div>
        ) : (
          <div className="divide-y">
            {data.map((job) => (
              <div key={job.job_id} className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="p-2 bg-background rounded-md border shadow-sm flex-shrink-0">
                    {getJobIcon(job.job_type)}
                  </div>
                  <div>
                    <h3 className="font-medium flex items-center gap-2">
                      {job.job_type.toUpperCase()}
                      <Badge variant="secondary" className="text-[10px] uppercase font-mono">{job.job_id.substring(0, 8)}</Badge>
                    </h3>
                    <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
                      <Clock className="w-3 h-3" />
                      {new Date(job.created_at * 1000).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div>
                  <Badge className={getStatusColor(job.status)} variant="outline">
                    {job.status.toUpperCase()}
                    {job.status === 'running' && <Loader2 className="w-3 h-3 ml-1 animate-spin" />}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default JobsPage;
