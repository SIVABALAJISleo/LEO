import { useState, useRef } from 'react';
import { hyperClient } from '@/lib/api';
import { useJobsData, CreateJobInput } from '@/hooks/useJobsData';
import { useModulesData } from '@/hooks/useModulesData';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Skeleton } from '@/components/ui/skeleton';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { useToast } from '@/hooks/use-toast';
import { Play, Upload, ChevronDown, Wand2, Clock, CheckCircle, XCircle, Loader2, Eye, RotateCw } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

const MODULE_NAMES = [
  'AdaptiveDowngrade', 'ProgressiveCompute', 'TemporalReconstruction', 'PerceptualValidation',
  'MixtureOfExperts', 'SemanticCache', 'VectorSearch', 'RateLimiting',
  'ChaosResilience', 'HardwareBalancing', 'TileSolver', 'ProbabilisticCore',
  'AsyncOffload', 'SelfProfiling', 'BehaviorEmulation'
];

const RECOMMENDED_MODULES = [
  'AdaptiveDowngrade', 'ProgressiveCompute', 'MixtureOfExperts',
  'SemanticCache', 'HardwareBalancing', 'SelfProfiling'
];

const InferencePage = () => {
  const { jobs, models, loading, createJob, cancelJob, retryJob, getJobById } = useJobsData();
  const { moduleConfigs } = useModulesData();
  const { toast } = useToast();

  const [selectedModel, setSelectedModel] = useState('');
  const [inputText, setInputText] = useState('');
  const [selectedModules, setSelectedModules] = useState<string[]>([]);
  const [priority, setPriority] = useState(5);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [batchSize, setBatchSize] = useState(1);
  const [timeout, setTimeoutVal] = useState(30000);
  const [callbackUrl, setCallbackUrl] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [detailJobId, setDetailJobId] = useState<string | null>(null);
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const activeJobs = jobs.filter(j => ['queued', 'running'].includes(j.status));
  const jobHistory = jobs.filter(j => !['queued', 'running'].includes(j.status)).slice(0, 20);

  const toggleModule = (moduleName: string) => {
    setSelectedModules(prev =>
      prev.includes(moduleName)
        ? prev.filter(m => m !== moduleName)
        : [...prev, moduleName]
    );
  };

  const applyRecommended = () => {
    setSelectedModules(RECOMMENDED_MODULES);
    toast({ title: 'Applied Recommended Modules', description: `${RECOMMENDED_MODULES.length} modules selected` });
  };

  const handleSubmit = async () => {
    if (!selectedModel) {
      toast({ title: 'Error', description: 'Please select a model', variant: 'destructive' });
      return;
    }
    if (!inputText.trim()) {
      toast({ title: 'Error', description: 'Please enter input text', variant: 'destructive' });
      return;
    }

    setIsSubmitting(true);
    try {
      const input: CreateJobInput = {
        model_id: selectedModel,
        priority,
        input_data: { text: inputText, batch_size: batchSize },
        enabled_modules: selectedModules,
        optimization_options: { timeout, callback_url: callbackUrl || undefined }
      };

      await createJob(input);
      setInputText('');
      setSelectedModules([]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBatchUpload = async () => {
    if (!batchFile) {
      toast({ title: 'Error', description: 'Please select a file', variant: 'destructive' });
      return;
    }

    const isCsv = batchFile.name.toLowerCase().endsWith('.csv');

    try {
      if (isCsv && selectedModel) {
        // Legacy Batch Support for CSV
        const text = await batchFile.text();
        const lines = text.split('\n').filter(l => l.trim());

        for (const line of lines.slice(0, 50)) {
          const input: CreateJobInput = {
            model_id: selectedModel,
            priority,
            input_data: { text: line, batch_size: batchSize },
            enabled_modules: selectedModules,
            optimization_options: { timeout }
          };
          await createJob(input);
        }
        toast({ title: 'Batch Created', description: `Created ${Math.min(lines.length, 50)} jobs from CSV` });
      } else {
        // Universal Document Ingestion for RAG
        const result = await hyperClient.uploadFile(batchFile);
        toast({
          title: 'Document Ingested',
          description: `Successfully ingested ${batchFile.name} (${result.content_length} chars) for RAG.`
        });
      }

      setBatchFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: any) {
      toast({ title: 'Error', description: err.message, variant: 'destructive' });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-primary" />;
      case 'failed': return <XCircle className="h-4 w-4 text-destructive" />;
      case 'running': return <Loader2 className="h-4 w-4 text-primary animate-spin" />;
      default: return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'default';
      case 'failed': return 'destructive';
      case 'running': return 'secondary';
      default: return 'outline';
    }
  };

  const selectedJob = detailJobId ? getJobById(detailJobId) : null;

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-[400px]" />
        <Skeleton className="h-[300px]" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Inference Jobs</h1>
        <p className="text-muted-foreground">Create and manage AI inference tasks</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* New Job Form */}
        <Card className="lg:col-span-2 bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Play className="h-5 w-5 text-primary" />
              New Inference Job
            </CardTitle>
            <CardDescription>Configure and submit a new inference task</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="model">Model</Label>
                <Select value={selectedModel} onValueChange={setSelectedModel}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a model" />
                  </SelectTrigger>
                  <SelectContent>
                    {models.map(m => (
                      <SelectItem key={m.id} value={m.id}>
                        {m.name} ({m.model_type})
                      </SelectItem>
                    ))}
                    {models.length === 0 && (
                      <SelectItem value="demo" disabled>No models available</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="priority">Priority (1-10)</Label>
                <Input
                  id="priority"
                  type="number"
                  min={1}
                  max={10}
                  value={priority}
                  onChange={e => setPriority(parseInt(e.target.value) || 5)}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="input">Input Text</Label>
              <Textarea
                id="input"
                placeholder="Enter your prompt or input data..."
                value={inputText}
                onChange={e => setInputText(e.target.value)}
                className="min-h-[120px]"
              />
            </div>

            {/* Modules Selection */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Optimization Modules</Label>
                <Button variant="outline" size="sm" onClick={applyRecommended}>
                  <Wand2 className="h-4 w-4 mr-2" />
                  Apply Recommended
                </Button>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
                {MODULE_NAMES.map(module => (
                  <div
                    key={module}
                    className={`flex items-center gap-2 p-2 rounded-md border cursor-pointer transition-colors ${selectedModules.includes(module)
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:border-primary/50'
                      }`}
                    onClick={() => toggleModule(module)}
                  >
                    <Checkbox
                      checked={selectedModules.includes(module)}
                      onCheckedChange={() => toggleModule(module)}
                    />
                    <span className="text-xs">{module.replace(/([A-Z])/g, ' $1').trim()}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Advanced Options */}
            <Collapsible open={showAdvanced} onOpenChange={setShowAdvanced}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between">
                  Advanced Options
                  <ChevronDown className={`h-4 w-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="space-y-4 pt-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="batchSize">Batch Size</Label>
                    <Input
                      id="batchSize"
                      type="number"
                      min={1}
                      max={64}
                      value={batchSize}
                      onChange={e => setBatchSize(parseInt(e.target.value) || 1)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="timeout">Timeout (ms)</Label>
                    <Input
                      id="timeout"
                      type="number"
                      min={1000}
                      value={timeout}
                      onChange={e => setTimeoutVal(parseInt(e.target.value) || 30000)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="callback">Callback URL</Label>
                    <Input
                      id="callback"
                      type="url"
                      placeholder="https://..."
                      value={callbackUrl}
                      onChange={e => setCallbackUrl(e.target.value)}
                    />
                  </div>
                </div>
              </CollapsibleContent>
            </Collapsible>

            <Button
              className="w-full"
              onClick={handleSubmit}
              disabled={isSubmitting || !selectedModel}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Submit Job
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Universal File Upload */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-primary" />
              Universal Ingestion
            </CardTitle>
            <CardDescription>Upload any file (PDF, DOCX, CSV) to context-enrich the engine</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-border rounded-lg p-6 text-center">
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.txt,.pdf,.docx"
                className="hidden"
                onChange={e => setBatchFile(e.target.files?.[0] || null)}
              />
              <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground mb-2">
                {batchFile ? batchFile.name : 'Drop any file here or click to browse'}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
              >
                Choose File
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Supports: PDF, DOCX, CSV, TXT. Documents will be indexed for RAG.
            </p>
            <Button
              className="w-full"
              onClick={handleBatchUpload}
              disabled={!batchFile}
            >
              <Upload className="h-4 w-4 mr-2" />
              {batchFile?.name.endsWith('.csv') ? 'Process Batch' : 'Ingest Document'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Active Jobs & History */}
      <Tabs defaultValue="active" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="active" className="flex items-center gap-2">
            Active Jobs
            {activeJobs.length > 0 && (
              <Badge variant="secondary">{activeJobs.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="history">Job History</TabsTrigger>
        </TabsList>

        <TabsContent value="active">
          <Card className="bg-card border-border">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead>Job ID</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead>Modules</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeJobs.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        No active jobs
                      </TableCell>
                    </TableRow>
                  ) : (
                    activeJobs.map(job => (
                      <TableRow key={job.id} className="border-border">
                        <TableCell className="font-mono text-sm">{job.id.slice(0, 8)}...</TableCell>
                        <TableCell>{job.model?.name || 'Unknown'}</TableCell>
                        <TableCell>
                          <Badge variant={getStatusColor(job.status)}>
                            <span className="flex items-center gap-1">
                              {getStatusIcon(job.status)}
                              {job.status}
                            </span>
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="w-24">
                            <Progress value={job.progress || 0} className="h-2" />
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {job.started_at ? formatDistanceToNow(new Date(job.started_at), { addSuffix: true }) : '-'}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {Array.isArray(job.enabled_modules) ? job.enabled_modules.length : 0} modules
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="sm" onClick={() => setDetailJobId(job.id)}>
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" onClick={() => cancelJob(job.id)}>
                              <XCircle className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="history">
          <Card className="bg-card border-border">
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead>Job ID</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Latency</TableHead>
                    <TableHead>Speedup</TableHead>
                    <TableHead>Completed</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobHistory.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        No job history
                      </TableCell>
                    </TableRow>
                  ) : (
                    jobHistory.map(job => (
                      <TableRow key={job.id} className="border-border">
                        <TableCell className="font-mono text-sm">{job.id.slice(0, 8)}...</TableCell>
                        <TableCell>{job.model?.name || 'Unknown'}</TableCell>
                        <TableCell>
                          <Badge variant={getStatusColor(job.status)}>
                            <span className="flex items-center gap-1">
                              {getStatusIcon(job.status)}
                              {job.status}
                            </span>
                          </Badge>
                        </TableCell>
                        <TableCell className="text-primary">
                          {job.latency_ms ? `${job.latency_ms}ms` : '-'}
                        </TableCell>
                        <TableCell className="text-primary">
                          {job.speedup ? `${job.speedup.toFixed(1)}x` : '-'}
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {job.completed_at ? format(new Date(job.completed_at), 'MMM d, HH:mm') : '-'}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="sm" onClick={() => setDetailJobId(job.id)}>
                              <Eye className="h-4 w-4" />
                            </Button>
                            {job.status === 'failed' && (
                              <Button variant="ghost" size="sm" onClick={() => retryJob(job.id)}>
                                <RotateCw className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Job Detail Modal */}
      <Dialog open={!!detailJobId} onOpenChange={() => setDetailJobId(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Job Details</DialogTitle>
          </DialogHeader>
          {selectedJob && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Job ID</Label>
                  <p className="font-mono text-sm">{selectedJob.id}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Status</Label>
                  <Badge variant={getStatusColor(selectedJob.status)} className="mt-1">
                    {selectedJob.status}
                  </Badge>
                </div>
                <div>
                  <Label className="text-muted-foreground">Model</Label>
                  <p>{selectedJob.model?.name || 'Unknown'}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Priority</Label>
                  <p>{selectedJob.priority}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Latency</Label>
                  <p className="text-primary">{selectedJob.latency_ms ? `${selectedJob.latency_ms}ms` : '-'}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Speedup</Label>
                  <p className="text-primary">{selectedJob.speedup ? `${selectedJob.speedup.toFixed(2)}x` : '-'}</p>
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground">Enabled Modules</Label>
                <div className="flex flex-wrap gap-1 mt-1">
                  {Array.isArray(selectedJob.enabled_modules) && selectedJob.enabled_modules.map((m: any) => (
                    <Badge key={m} variant="outline">{m}</Badge>
                  ))}
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground">Input Data</Label>
                <pre className="mt-1 p-3 bg-muted rounded-md text-sm overflow-x-auto">
                  {JSON.stringify(selectedJob.input_data, null, 2)}
                </pre>
              </div>

              {selectedJob.output_data && (
                <div>
                  <Label className="text-muted-foreground">Output Data</Label>
                  <pre className="mt-1 p-3 bg-muted rounded-md text-sm overflow-x-auto">
                    {JSON.stringify(selectedJob.output_data, null, 2)}
                  </pre>
                </div>
              )}

              {selectedJob.error_message && (
                <div>
                  <Label className="text-muted-foreground">Error</Label>
                  <p className="mt-1 text-destructive">{selectedJob.error_message}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                <div>Created: {format(new Date(selectedJob.created_at), 'PPpp')}</div>
                {selectedJob.started_at && <div>Started: {format(new Date(selectedJob.started_at), 'PPpp')}</div>}
                {selectedJob.completed_at && <div>Completed: {format(new Date(selectedJob.completed_at), 'PPpp')}</div>}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default InferencePage;
