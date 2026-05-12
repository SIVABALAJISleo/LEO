import { useState } from 'react';
import { useResultsData } from '@/hooks/useResultsData';
import { InferenceJob } from '@/hooks/useJobsData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Skeleton } from '@/components/ui/skeleton';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Search, Download, Eye, GitCompare, CheckCircle, XCircle, Filter } from 'lucide-react';
import { format } from 'date-fns';

const ResultsPage = () => {
  const {
    loading,
    completedJobs,
    selectedJobs,
    toggleJobSelection,
    clearSelection,
    getSelectedJobsData,
    exportToJson,
    exportToCsv
  } = useResultsData();

  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [detailJob, setDetailJob] = useState<InferenceJob | null>(null);
  const [showComparison, setShowComparison] = useState(false);

  const filteredJobs = completedJobs.filter(job => {
    const matchesSearch = job.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.model?.name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || job.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const comparisonJobs = getSelectedJobsData();

  // Stats for detail view
  const getJobStats = (job: InferenceJob) => {
    const modules = Array.isArray(job.enabled_modules) ? job.enabled_modules : [];
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      moduleDistribution: modules.map((m: any) => ({ name: m, value: 1 })),
      metrics: [
        { name: 'Latency', value: job.latency_ms || 0 },
        { name: 'Speedup', value: (job.speedup || 1) * 100 },
        { name: 'Compression', value: (job.compression_ratio || 1) * 100 },
      ]
    };
  };

  const CHART_COLORS = [
    'hsl(var(--primary))',
    'hsl(88 72% 60%)',
    'hsl(200 80% 50%)',
    'hsl(280 70% 50%)',
    'hsl(30 80% 50%)',
  ];

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-16" />
        <Skeleton className="h-[400px]" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">Inference Results</h1>
          <p className="text-muted-foreground">Browse and analyze completed jobs</p>
        </div>
        <div className="flex items-center gap-2">
          {selectedJobs.length > 0 && (
            <>
              <Badge variant="secondary">{selectedJobs.length} selected</Badge>
              <Button variant="outline" size="sm" onClick={() => setShowComparison(true)}>
                <GitCompare className="h-4 w-4 mr-2" />
                Compare
              </Button>
              <Button variant="outline" size="sm" onClick={clearSelection}>
                Clear
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Filters */}
      <Card className="bg-card border-border">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by job ID or model..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={() => exportToCsv(filteredJobs)}>
              <Download className="h-4 w-4 mr-2" />
              CSV
            </Button>
            <Button variant="outline" onClick={() => exportToJson(filteredJobs)}>
              <Download className="h-4 w-4 mr-2" />
              JSON
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Results Table */}
      <Card className="bg-card border-border">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-border">
                <TableHead className="w-10"></TableHead>
                <TableHead>Job ID</TableHead>
                <TableHead>Model</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Latency</TableHead>
                <TableHead>Speedup</TableHead>
                <TableHead>Compression</TableHead>
                <TableHead>Completed</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredJobs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center py-12 text-muted-foreground">
                    No completed jobs found
                  </TableCell>
                </TableRow>
              ) : (
                filteredJobs.map(job => (
                  <TableRow key={job.id} className="border-border">
                    <TableCell>
                      <Checkbox
                        checked={selectedJobs.includes(job.id)}
                        onCheckedChange={() => toggleJobSelection(job.id)}
                      />
                    </TableCell>
                    <TableCell className="font-mono text-sm">{job.id.slice(0, 8)}...</TableCell>
                    <TableCell>{job.model?.name || 'Unknown'}</TableCell>
                    <TableCell>
                      <Badge variant={job.status === 'completed' ? 'default' : 'destructive'}>
                        <span className="flex items-center gap-1">
                          {job.status === 'completed' ?
                            <CheckCircle className="h-3 w-3" /> :
                            <XCircle className="h-3 w-3" />
                          }
                          {job.status}
                        </span>
                      </Badge>
                    </TableCell>
                    <TableCell className="text-primary">
                      {job.latency_ms ? `${job.latency_ms}ms` : '-'}
                    </TableCell>
                    <TableCell className="text-primary">
                      {job.speedup ? `${job.speedup.toFixed(2)}x` : '-'}
                    </TableCell>
                    <TableCell>
                      {job.compression_ratio ? `${job.compression_ratio.toFixed(2)}x` : '-'}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {job.completed_at ? format(new Date(job.completed_at), 'MMM d, HH:mm') : '-'}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" onClick={() => setDetailJob(job)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Detail Modal */}
      <Dialog open={!!detailJob} onOpenChange={() => setDetailJob(null)}>
        <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center justify-between">
              <span>Job Results</span>
              {detailJob && (
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => exportToJson([detailJob])}>
                    <Download className="h-4 w-4 mr-2" />
                    JSON
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => exportToCsv([detailJob])}>
                    <Download className="h-4 w-4 mr-2" />
                    CSV
                  </Button>
                </div>
              )}
            </DialogTitle>
          </DialogHeader>
          {detailJob && (
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="mb-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="data">Input/Output</TabsTrigger>
                <TabsTrigger value="metrics">Metrics</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <Card className="bg-muted/50">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-muted-foreground">Latency</p>
                      <p className="text-2xl font-bold text-primary">{detailJob.latency_ms || 0}ms</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-muted/50">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-muted-foreground">Speedup</p>
                      <p className="text-2xl font-bold text-primary">{detailJob.speedup?.toFixed(2) || 1}x</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-muted/50">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-muted-foreground">Compression</p>
                      <p className="text-2xl font-bold text-primary">{detailJob.compression_ratio?.toFixed(2) || 1}x</p>
                    </CardContent>
                  </Card>
                  <Card className="bg-muted/50">
                    <CardContent className="p-4 text-center">
                      <p className="text-sm text-muted-foreground">Modules Used</p>
                      <p className="text-2xl font-bold text-primary">
                        {Array.isArray(detailJob.enabled_modules) ? detailJob.enabled_modules.length : 0}
                      </p>
                    </CardContent>
                  </Card>
                </div>

                <div>
                  <h3 className="font-medium mb-2">Enabled Modules</h3>
                  <div className="flex flex-wrap gap-2">
                    {Array.isArray(detailJob.enabled_modules) && detailJob.enabled_modules.map((m: string) => (
                      <Badge key={m} variant="outline">{m}</Badge>
                    ))}
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="data" className="space-y-4">
                <div>
                  <h3 className="font-medium mb-2">Input Data</h3>
                  <pre className="p-4 bg-muted rounded-lg text-sm overflow-x-auto max-h-[200px]">
                    {JSON.stringify(detailJob.input_data, null, 2)}
                  </pre>
                </div>
                {detailJob.output_data && (
                  <div>
                    <h3 className="font-medium mb-2">Output Data</h3>
                    <pre className="p-4 bg-muted rounded-lg text-sm overflow-x-auto max-h-[200px]">
                      {JSON.stringify(detailJob.output_data, null, 2)}
                    </pre>
                  </div>
                )}
                {detailJob.error_message && (
                  <div>
                    <h3 className="font-medium mb-2 text-destructive">Error</h3>
                    <pre className="p-4 bg-destructive/10 rounded-lg text-sm text-destructive">
                      {detailJob.error_message}
                    </pre>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="metrics">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card className="bg-muted/30">
                    <CardHeader>
                      <CardTitle className="text-sm">Performance Metrics</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[200px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={getJobStats(detailJob).metrics}>
                            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                            <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                            <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                            <Tooltip
                              contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                border: '1px solid hsl(var(--border))'
                              }}
                            />
                            <Bar dataKey="value" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-muted/30">
                    <CardHeader>
                      <CardTitle className="text-sm">Module Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-[200px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <PieChart>
                            <Pie
                              data={getJobStats(detailJob).moduleDistribution}
                              dataKey="value"
                              nameKey="name"
                              cx="50%"
                              cy="50%"
                              outerRadius={70}
                              label={({ name }) => name.slice(0, 8)}
                              labelLine={false}
                            >
                              {getJobStats(detailJob).moduleDistribution.map((_, index) => (
                                <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>

      {/* Comparison Modal */}
      <Dialog open={showComparison} onOpenChange={setShowComparison}>
        <DialogContent className="max-w-5xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Job Comparison</DialogTitle>
          </DialogHeader>
          {comparisonJobs.length > 0 && (
            <div className="space-y-6">
              <Table>
                <TableHeader>
                  <TableRow className="border-border">
                    <TableHead>Metric</TableHead>
                    {comparisonJobs.map(job => (
                      <TableHead key={job.id}>{job.id.slice(0, 8)}...</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow className="border-border">
                    <TableCell className="font-medium">Model</TableCell>
                    {comparisonJobs.map(job => (
                      <TableCell key={job.id}>{job.model?.name || 'Unknown'}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow className="border-border">
                    <TableCell className="font-medium">Latency</TableCell>
                    {comparisonJobs.map(job => (
                      <TableCell key={job.id} className="text-primary">{job.latency_ms || 0}ms</TableCell>
                    ))}
                  </TableRow>
                  <TableRow className="border-border">
                    <TableCell className="font-medium">Speedup</TableCell>
                    {comparisonJobs.map(job => (
                      <TableCell key={job.id} className="text-primary">{job.speedup?.toFixed(2) || 1}x</TableCell>
                    ))}
                  </TableRow>
                  <TableRow className="border-border">
                    <TableCell className="font-medium">Compression</TableCell>
                    {comparisonJobs.map(job => (
                      <TableCell key={job.id}>{job.compression_ratio?.toFixed(2) || 1}x</TableCell>
                    ))}
                  </TableRow>
                  <TableRow className="border-border">
                    <TableCell className="font-medium">Modules</TableCell>
                    {comparisonJobs.map(job => (
                      <TableCell key={job.id}>
                        {Array.isArray(job.enabled_modules) ? job.enabled_modules.length : 0}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableBody>
              </Table>

              <Card className="bg-muted/30">
                <CardHeader>
                  <CardTitle className="text-sm">Performance Comparison</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[250px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={comparisonJobs.map(j => ({
                        name: j.id.slice(0, 8),
                        latency: j.latency_ms || 0,
                        speedup: (j.speedup || 1) * 100
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                        <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                        <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                        <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }} />
                        <Legend />
                        <Bar dataKey="latency" name="Latency (ms)" fill="hsl(var(--primary))" />
                        <Bar dataKey="speedup" name="Speedup %" fill="hsl(88 72% 60%)" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ResultsPage;
