import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import { useObservabilityData } from '@/hooks/useObservabilityData';
import { LoadingState } from '@/components/ui/loading-state';
import { EmptyState } from '@/components/ui/empty-state';

const ObservabilityPage = () => {
  const { metricsRaw, traces, anomalies, correlations, isLoading, resolveAnomaly, getAnomalyStats } = useObservabilityData();
  const stats = getAnomalyStats();

  if (isLoading) return <LoadingState message="Loading observability data..." />;

  return (
    <div className="space-y-6 p-6">
      <div><h1 className="text-3xl font-bold">Observability & Telemetry</h1><p className="text-muted-foreground">Full metrics, distributed tracing, and anomaly detection</p></div>
      
      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Metrics</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{metricsRaw.length}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Traces</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{traces.length}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Anomalies</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold text-destructive">{stats.unresolved}</p></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm">Correlations</CardTitle></CardHeader><CardContent><p className="text-2xl font-bold">{correlations.length}</p></CardContent></Card>
      </div>

      <Tabs defaultValue="anomalies">
        <TabsList><TabsTrigger value="anomalies">Anomalies</TabsTrigger><TabsTrigger value="traces">Traces</TabsTrigger><TabsTrigger value="metrics">Metrics</TabsTrigger></TabsList>
        
        <TabsContent value="anomalies">{anomalies.length === 0 ? <EmptyState title="No anomalies" description="System is healthy" icon={Activity} /> : anomalies.map(a => (
          <Card key={a.id} className="mb-2"><CardContent className="flex justify-between items-center py-3">
            <div className="flex items-center gap-3">{a.is_resolved ? <CheckCircle className="text-primary h-5 w-5" /> : <AlertTriangle className="text-destructive h-5 w-5" />}<div><p className="font-medium">{a.metric_name}</p><p className="text-sm text-muted-foreground">{a.anomaly_type} • {a.deviation_percent?.toFixed(1)}% deviation</p></div></div>
            <div className="flex items-center gap-2"><Badge variant={a.severity === 'critical' ? 'destructive' : a.severity === 'high' ? 'default' : 'secondary'}>{a.severity}</Badge>{!a.is_resolved && <Button size="sm" onClick={() => resolveAnomaly(a.id)}>Resolve</Button>}</div>
          </CardContent></Card>
        ))}</TabsContent>
        
        <TabsContent value="traces">{traces.length === 0 ? <EmptyState title="No traces" description="No distributed traces recorded" /> : traces.slice(0, 20).map(t => (
          <Card key={t.id} className="mb-2"><CardContent className="grid grid-cols-4 gap-4 py-3 text-sm"><div><span className="text-muted-foreground">Operation:</span> {t.operation_name}</div><div><span className="text-muted-foreground">Service:</span> {t.service_name || 'N/A'}</div><div><span className="text-muted-foreground">Duration:</span> {t.duration_ms}ms</div><div><Badge variant={t.status === 'ok' ? 'secondary' : 'destructive'}>{t.status}</Badge></div></CardContent></Card>
        ))}</TabsContent>
        
        <TabsContent value="metrics">{metricsRaw.length === 0 ? <EmptyState title="No metrics" description="No raw metrics recorded" /> : (
          <div className="grid gap-2">{metricsRaw.slice(0, 20).map(m => <Card key={m.id}><CardContent className="flex justify-between py-3"><span className="font-medium">{m.metric_name}</span><span className="text-primary font-bold">{m.metric_value}</span></CardContent></Card>)}</div>
        )}</TabsContent>
      </Tabs>
    </div>
  );
};

export default ObservabilityPage;
