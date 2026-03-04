import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Database, Zap, Trash2, RefreshCw, Flame, Play } from 'lucide-react';
import { useCachingData, CACHE_LEVELS, INVALIDATION_TYPES } from '@/hooks/useCachingData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const CachingPage = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { cacheMetadata, analytics, invalidationLogs, warmingJobs, isLoading, invalidateCache, startWarmingJob, getHitRateByLevel, getTotalSizeByLevel, getTopCachedQueries, getEstimatedSpeedup } = useCachingData();
  const [selectedLevel, setSelectedLevel] = useState('L1');
  const [invalidationType, setInvalidationType] = useState('manual');

  const handleInvalidate = async () => {
    await invalidateCache(selectedLevel, invalidationType, 'Manual invalidation');
  };

  const handleWarm = async () => {
    await startWarmingJob({ job_type: 'manual', target_cache_level: selectedLevel, items_to_warm: 100, trigger_reason: 'Manual warming' });
  };

  if (isLoading) return <LoadingState message="Loading cache data..." />;

  const hitRateData = CACHE_LEVELS.map(l => ({ name: l.value, hitRate: getHitRateByLevel(l.value), size: getTotalSizeByLevel(l.value) / (1024 * 1024) }));
  const topQueries = getTopCachedQueries(5);
  const COLORS = ['hsl(var(--primary))', 'hsl(var(--chart-2))', 'hsl(var(--chart-3))'];

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Advanced Caching</h1>
          <p className="text-muted-foreground">Multi-level cache with semantic matching</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {CACHE_LEVELS.map((level) => (
          <Card key={level.value}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm flex items-center gap-2"><Database className="h-4 w-4" />{level.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{getHitRateByLevel(level.value).toFixed(1)}%</p>
              <p className="text-xs text-muted-foreground">Hit Rate • {(getTotalSizeByLevel(level.value) / (1024 * 1024)).toFixed(2)} MB</p>
              <p className="text-xs text-muted-foreground mt-1">{level.policy} • TTL: {level.ttl}</p>
            </CardContent>
          </Card>
        ))}
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-2"><Zap className="h-4 w-4" />Time Saved</CardTitle></CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-500">{getEstimatedSpeedup().toFixed(1)}s</p>
            <p className="text-xs text-muted-foreground">Total response time saved</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="entries">Cache Entries</TabsTrigger>
          <TabsTrigger value="warming">Cache Warming</TabsTrigger>
          <TabsTrigger value="logs">Invalidation Logs</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Hit Rate by Level</CardTitle></CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={hitRateData}>
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="hitRate" fill="hsl(var(--primary))" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
            <Card>
              <CardHeader><CardTitle>Cache Distribution</CardTitle></CardHeader>
              <CardContent className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={hitRateData} dataKey="size" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                      {hitRateData.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader><CardTitle>Top Cached Queries</CardTitle></CardHeader>
            <CardContent>
              {topQueries.length === 0 ? <EmptyState title="No cached queries" /> : (
                <div className="space-y-2">
                  {topQueries.map((query) => (
                    <div key={query.id} className="flex items-center justify-between p-2 border rounded">
                      <div>
                        <p className="font-medium font-mono text-sm">{query.cache_key.slice(0, 50)}...</p>
                        <p className="text-xs text-muted-foreground">{query.cache_level} • {query.content_type}</p>
                      </div>
                      <Badge>{query.hit_count} hits</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="entries">
          <Card>
            <CardHeader>
              <CardTitle>Cache Management</CardTitle>
              <CardDescription>Invalidate or warm cache levels</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                  <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
                  <SelectContent>{CACHE_LEVELS.map((l) => <SelectItem key={l.value} value={l.value}>{l.label}</SelectItem>)}</SelectContent>
                </Select>
                <Select value={invalidationType} onValueChange={setInvalidationType}>
                  <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
                  <SelectContent>{INVALIDATION_TYPES.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent>
                </Select>
                <Button variant="destructive" onClick={handleInvalidate}><Trash2 className="mr-2 h-4 w-4" />Invalidate</Button>
                <Button onClick={handleWarm}><Flame className="mr-2 h-4 w-4" />Warm Cache</Button>
              </div>
              
              <div className="space-y-2">
                {cacheMetadata.filter(c => c.cache_level === selectedLevel).slice(0, 10).map((entry) => (
                  <div key={entry.id} className="flex items-center justify-between p-2 border rounded text-sm">
                    <span className="font-mono">{entry.cache_key.slice(0, 40)}...</span>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{entry.hit_count} hits</Badge>
                      <span className="text-muted-foreground">{((entry.size_bytes || 0) / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="warming">
          <Card>
            <CardHeader><CardTitle>Cache Warming Jobs</CardTitle></CardHeader>
            <CardContent>
              {warmingJobs.length === 0 ? <EmptyState title="No warming jobs" /> : warmingJobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 border rounded mb-2">
                  <div>
                    <p className="font-medium">{job.job_type} - {job.target_cache_level}</p>
                    <p className="text-sm text-muted-foreground">{job.trigger_reason}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <Progress value={(job.items_warmed / (job.items_to_warm || 1)) * 100} className="w-24" />
                    <Badge>{job.status}</Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs">
          <Card>
            <CardHeader><CardTitle>Invalidation History</CardTitle></CardHeader>
            <CardContent>
              {invalidationLogs.length === 0 ? <EmptyState title="No invalidation logs" /> : invalidationLogs.map((log) => (
                <div key={log.id} className="flex items-center justify-between p-2 border-b text-sm">
                  <div>
                    <p className="font-medium">{log.invalidation_type} on {log.cache_level}</p>
                    <p className="text-muted-foreground">{log.reason}</p>
                  </div>
                  <div className="text-right">
                    <p>{log.affected_keys} keys</p>
                    <p className="text-xs text-muted-foreground">{new Date(log.created_at).toLocaleString()}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CachingPage;
