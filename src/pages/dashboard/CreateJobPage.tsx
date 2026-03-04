import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useGpuJobs } from '@/hooks/useGpuJobs';
import { JOB_TYPE_OPTIONS } from '@/lib/gpuJobTypes';
import { 
  ArrowLeft, 
  Zap, 
  Cpu, 
  Monitor, 
  Server,
  Loader2,
  Info,
  AlertTriangle
} from 'lucide-react';

type JobTier = 'light' | 'medium' | 'heavy' | 'very_heavy';

const TIER_INFO: Record<JobTier, { 
  label: string; 
  description: string; 
  icon: React.ElementType; 
  color: string;
  examples: string[];
  warning?: string;
}> = {
  light: {
    label: 'Light',
    description: 'Instant results',
    icon: Zap,
    color: 'text-green-500',
    examples: ['Text analysis', 'Validation', 'Quick tasks'],
  },
  medium: {
    label: 'Medium',
    description: 'Fast processing in your browser',
    icon: Monitor,
    color: 'text-yellow-500',
    examples: ['Image processing', 'Data transformation'],
  },
  heavy: {
    label: 'Heavy',
    description: 'Full quality processing (may take a few minutes)',
    icon: Server,
    color: 'text-red-500',
    examples: ['Training', 'Rendering', 'Complex tasks'],
  },
  very_heavy: {
    label: 'Very Heavy',
    description: 'Estimated projections and simulations',
    icon: Cpu,
    color: 'text-purple-500',
    examples: ['Large training', 'HD rendering', 'Massive simulation'],
    warning: 'This tier provides estimates and projections.',
  },
};

export default function CreateJobPage() {
  const navigate = useNavigate();
  const { createJob, getMemoryReport, systemStatus } = useGpuJobs();
  
  const [jobName, setJobName] = useState('');
  const [jobType, setJobType] = useState('');
  const [jobTier, setJobTier] = useState<JobTier>('heavy');
  const [payload, setPayload] = useState('{}');
  const [priority, setPriority] = useState([5]);
  const [memoryMb, setMemoryMb] = useState(4096);
  const [estimatedDuration, setEstimatedDuration] = useState(300);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const memoryReport = getMemoryReport();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const selectedJobType = JOB_TYPE_OPTIONS.find(j => j.value === jobType);
  const tierInfo = TIER_INFO[jobTier];

  const handleJobTypeChange = (value: string) => {
    setJobType(value);
    const option = JOB_TYPE_OPTIONS.find(j => j.value === value);
    if (option) {
      setMemoryMb(option.memoryEstimate);
    }
  };

  const handleSubmit = async () => {
    setError(null);
    setIsSubmitting(true);

    try {
      // Validate payload JSON
      let parsedPayload;
      try {
        parsedPayload = JSON.parse(payload);
      } catch {
        throw new Error('Invalid JSON payload');
      }

      const job = await createJob({
        job_type: jobType,
        job_name: jobName || `${jobType} Job`,
        payload: parsedPayload,
        priority: priority[0],
        memory_required_mb: jobTier === 'heavy' ? memoryMb : undefined,
        estimated_duration_sec: estimatedDuration,
      });

      if (job) {
        navigate(`/dashboard/jobs`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create job');
    } finally {
      setIsSubmitting(false);
    }
  };

  const isValid = jobType && jobName;
  const memoryExceedsLimit = memoryMb > memoryReport.max_job_size_mb;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Create New Job</h1>
          <p className="text-muted-foreground">Configure and submit a compute job</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Job Details */}
          <Card>
            <CardHeader>
              <CardTitle>Job Details</CardTitle>
              <CardDescription>Basic information about your job</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Job Name</Label>
                <Input
                  id="name"
                  placeholder="My Training Job"
                  value={jobName}
                  onChange={(e) => setJobName(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="type">Job Type</Label>
                <Select value={jobType} onValueChange={handleJobTypeChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select job type" />
                  </SelectTrigger>
                  <SelectContent>
                    {JOB_TYPE_OPTIONS.map(option => (
                      <SelectItem key={option.value} value={option.value}>
                        <div className="flex items-center justify-between w-full">
                          <span>{option.label}</span>
                          <span className="text-xs text-muted-foreground ml-4">
                            ~{(option.memoryEstimate / 1024).toFixed(0)}GB
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="payload">Payload (JSON)</Label>
                <Textarea
                  id="payload"
                  placeholder='{"prompt": "Hello world"}'
                  value={payload}
                  onChange={(e) => setPayload(e.target.value)}
                  className="font-mono text-sm h-32"
                />
              </div>
            </CardContent>
          </Card>

          {/* Job Tier Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Processing Tier</CardTitle>
              <CardDescription>Choose where your job runs</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                {(Object.entries(TIER_INFO) as [JobTier, typeof tierInfo][]).map(([tier, info]) => (
                  <Card
                    key={tier}
                    className={`cursor-pointer transition-all ${
                      jobTier === tier 
                        ? 'border-primary ring-2 ring-primary/20' 
                        : 'hover:border-muted-foreground/50'
                    }`}
                    onClick={() => setJobTier(tier)}
                  >
                    <CardContent className="pt-4">
                      <div className="flex items-center gap-2 mb-2">
                        <info.icon className={`h-5 w-5 ${info.color}`} />
                        <span className="font-semibold">{info.label}</span>
                      </div>
                      <p className="text-xs text-muted-foreground mb-3">
                        {info.description}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {info.examples.map((ex, i) => (
                          <Badge key={i} variant="outline" className="text-xs">
                            {ex}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Heavy Job Options */}
          {jobTier === 'heavy' && (
            <Card>
              <CardHeader>
                <CardTitle>Heavy Job Configuration</CardTitle>
                <CardDescription>GPU resource requirements</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Priority</Label>
                    <span className="text-sm text-muted-foreground">
                      {priority[0]} / 10
                    </span>
                  </div>
                  <Slider
                    value={priority}
                    onValueChange={setPriority}
                    min={1}
                    max={10}
                    step={1}
                  />
                  <p className="text-xs text-muted-foreground">
                    Higher priority jobs are processed first
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>GPU Memory Required</Label>
                    <span className={`text-sm ${memoryExceedsLimit ? 'text-destructive' : 'text-muted-foreground'}`}>
                      {(memoryMb / 1024).toFixed(1)} GB
                    </span>
                  </div>
                  <Slider
                    value={[memoryMb]}
                    onValueChange={(v) => setMemoryMb(v[0])}
                    min={1024}
                    max={24576}
                    step={512}
                  />
                  {memoryExceedsLimit && (
                    <p className="text-xs text-destructive flex items-center gap-1">
                      <AlertTriangle className="h-3 w-3" />
                      Exceeds available VRAM ({(memoryReport.max_job_size_mb / 1024).toFixed(1)}GB max)
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Estimated Duration</Label>
                    <span className="text-sm text-muted-foreground">
                      {Math.floor(estimatedDuration / 60)}m {estimatedDuration % 60}s
                    </span>
                  </div>
                  <Slider
                    value={[estimatedDuration]}
                    onValueChange={(v) => setEstimatedDuration(v[0])}
                    min={60}
                    max={7200}
                    step={60}
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div className="flex gap-4">
            <Button
              className="flex-1"
              size="lg"
              onClick={handleSubmit}
              disabled={!isValid || isSubmitting || (jobTier === 'heavy' && memoryExceedsLimit)}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Cpu className="h-4 w-4 mr-2" />
                  Create Job
                </>
              )}
            </Button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Selected Tier Info */}
          <Card className={`border-${tierInfo.color.replace('text-', '')}/30`}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <tierInfo.icon className={`h-5 w-5 ${tierInfo.color}`} />
                {tierInfo.label} Job
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <p className="text-muted-foreground">{tierInfo.description}</p>
              
              {jobTier === 'light' && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Light jobs complete immediately. Results are returned in the response.
                  </AlertDescription>
                </Alert>
              )}
              
              {jobTier === 'medium' && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Medium jobs run in your browser. Keep the tab open until completion.
                  </AlertDescription>
                </Alert>
              )}
              
              {jobTier === 'heavy' && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    Heavy jobs are queued and processed by the HYPER agent when available.
                  </AlertDescription>
                </Alert>
              )}
              
              {jobTier === 'very_heavy' && (
                <Alert className="border-purple-500/30 bg-purple-500/5">
                  <AlertTriangle className="h-4 w-4 text-purple-500" />
                  <AlertDescription className="text-purple-300">
                    {tierInfo.warning}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* System Status */}
          {jobTier === 'heavy' && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">System Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Worker Status</span>
                  <Badge variant={systemStatus?.is_online ? 'default' : 'destructive'}>
                    {systemStatus?.is_online ? 'Online' : 'Offline'}
                  </Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">GPU Temp</span>
                  <span>{systemStatus?.gpu_temperature_celsius || 0}°C</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Available VRAM</span>
                  <span>{(memoryReport.available_mb / 1024).toFixed(1)} GB</span>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
