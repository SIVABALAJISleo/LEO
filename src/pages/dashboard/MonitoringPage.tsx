import { useState } from 'react';
import { useMonitoringData } from '@/hooks/useMonitoringData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, Legend } from 'recharts';
import { Activity, Zap, Database, Cpu, RefreshCw, Download, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { format } from 'date-fns';

const MonitoringPage = () => {
  const { 
    loading, 
    performanceMetrics, 
    systemMetrics, 
    alerts, 
    moduleConfigs, 
    kpis,
    dateRange,
    setDateRange,
    refreshAll,
    resolveAlert 
  } = useMonitoringData();
  
  const [chartType, setChartType] = useState<'latency' | 'throughput' | 'system'>('latency');
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Date range options
  const dateRanges = [
    { label: 'Last Hour', value: '1h', ms: 60 * 60 * 1000 },
    { label: 'Last 6 Hours', value: '6h', ms: 6 * 60 * 60 * 1000 },
    { label: 'Last 24 Hours', value: '24h', ms: 24 * 60 * 60 * 1000 },
    { label: 'Last 7 Days', value: '7d', ms: 7 * 24 * 60 * 60 * 1000 },
  ];

  const handleDateRangeChange = (value: string) => {
    const range = dateRanges.find(r => r.value === value);
    if (range) {
      setDateRange({
        start: new Date(Date.now() - range.ms),
        end: new Date()
      });
    }
  };

  // Prepare chart data
  const latencyChartData = performanceMetrics
    .filter(m => m.latency_ms)
    .slice(0, 50)
    .reverse()
    .map(m => ({
      time: format(new Date(m.recorded_at), 'HH:mm'),
      latency: m.latency_ms,
      throughput: m.throughput_rps
    }));

  const systemChartData = systemMetrics
    .slice(0, 24)
    .reverse()
    .map(m => ({
      time: format(new Date(m.recorded_at), 'HH:mm'),
      cpu: m.cpu_percent || 0,
      memory: m.memory_usage || 0,
      gpu: m.gpu_utilization || 0
    }));

  const moduleSpeedupData = moduleConfigs
    .filter(m => m.speedup_achieved)
    .map(m => ({
      name: m.module_name.replace(/([A-Z])/g, ' $1').trim(),
      speedup: m.speedup_achieved,
      compression: m.compression_ratio_achieved
    }));

  const exportData = (format: 'csv' | 'json') => {
    const data = { performanceMetrics, systemMetrics, alerts, kpis };
    
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `monitoring-data-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
    } else {
      const rows = performanceMetrics.map(m => 
        `${m.recorded_at},${m.metric_name},${m.metric_value},${m.latency_ms || ''},${m.throughput_rps || ''}`
      );
      const csv = ['timestamp,metric_name,value,latency_ms,throughput_rps', ...rows].join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `monitoring-data-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'destructive';
      case 'warning': return 'secondary';
      default: return 'outline';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical': return <XCircle className="h-4 w-4 text-destructive" />;
      case 'warning': return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default: return <Activity className="h-4 w-4 text-primary" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <Skeleton className="h-80" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header with controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold">System Monitoring</h1>
          <p className="text-muted-foreground">Real-time performance metrics and alerts</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Select defaultValue="24h" onValueChange={handleDateRangeChange}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {dateRanges.map(r => (
                <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={refreshAll}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={() => exportData('csv')}>
            <Download className="h-4 w-4 mr-2" />
            CSV
          </Button>
          <Button variant="outline" size="sm" onClick={() => exportData('json')}>
            <Download className="h-4 w-4 mr-2" />
            JSON
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Latency</p>
                <p className="text-3xl font-bold text-primary">{kpis.avgLatency.toFixed(1)}ms</p>
              </div>
              <Activity className="h-10 w-10 text-primary/30" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Throughput</p>
                <p className="text-3xl font-bold text-primary">{kpis.avgThroughput.toFixed(0)} req/s</p>
              </div>
              <Zap className="h-10 w-10 text-primary/30" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Cache Hit Rate</p>
                <p className="text-3xl font-bold text-primary">{(kpis.avgCacheHit * 100).toFixed(1)}%</p>
              </div>
              <Database className="h-10 w-10 text-primary/30" />
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active Modules</p>
                <p className="text-3xl font-bold text-primary">{kpis.activeModules}</p>
              </div>
              <Cpu className="h-10 w-10 text-primary/30" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <Card className="bg-card border-border">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Performance Metrics</CardTitle>
            <Select value={chartType} onValueChange={(v) => setChartType(v as any)}>
              <SelectTrigger className="w-[130px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="latency">Latency</SelectItem>
                <SelectItem value="throughput">Throughput</SelectItem>
                <SelectItem value="system">System</SelectItem>
              </SelectContent>
            </Select>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              {chartType === 'system' ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={systemChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'hsl(var(--card))', 
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px'
                      }} 
                    />
                    <Legend />
                    <Area type="monotone" dataKey="cpu" name="CPU %" stroke="hsl(var(--primary))" fill="hsl(var(--primary) / 0.2)" />
                    <Area type="monotone" dataKey="memory" name="Memory %" stroke="hsl(88 72% 60%)" fill="hsl(88 72% 60% / 0.2)" />
                    <Area type="monotone" dataKey="gpu" name="GPU %" stroke="hsl(200 80% 50%)" fill="hsl(200 80% 50% / 0.2)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={latencyChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: 'hsl(var(--card))', 
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px'
                      }} 
                    />
                    <Line 
                      type="monotone" 
                      dataKey={chartType} 
                      stroke="hsl(var(--primary))" 
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Module Speedups Chart */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Module Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={moduleSpeedupData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                  <XAxis type="number" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis dataKey="name" type="category" width={120} stroke="hsl(var(--muted-foreground))" fontSize={11} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--card))', 
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }} 
                  />
                  <Bar dataKey="speedup" name="Speedup x" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tables Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Module Performance Table */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle>Module Status</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="border-border">
                  <TableHead>Module</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Speedup</TableHead>
                  <TableHead className="text-right">Compression</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {moduleConfigs.slice(0, 8).map(module => (
                  <TableRow key={module.id} className="border-border">
                    <TableCell className="font-medium">{module.module_name}</TableCell>
                    <TableCell>
                      <Badge variant={module.enabled ? 'default' : 'secondary'}>
                        {module.enabled ? 'Active' : 'Disabled'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right text-primary">
                      {module.speedup_achieved ? `${module.speedup_achieved.toFixed(1)}x` : '-'}
                    </TableCell>
                    <TableCell className="text-right">
                      {module.compression_ratio_achieved ? `${module.compression_ratio_achieved.toFixed(1)}x` : '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Alerts Table */}
        <Card className="bg-card border-border">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Recent Alerts</span>
              <Badge variant="outline">{alerts.filter(a => !a.resolved).length} active</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="border-border">
                  <TableHead>Alert</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {alerts.slice(0, 6).map(alert => (
                  <TableRow key={alert.id} className="border-border">
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getSeverityIcon(alert.severity)}
                        <span className="font-medium">{alert.title}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {format(new Date(alert.created_at), 'HH:mm')}
                    </TableCell>
                    <TableCell>
                      {!alert.resolved && (
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => resolveAlert(alert.id)}
                        >
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MonitoringPage;
