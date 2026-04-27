import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { TrendingUp, Zap, DollarSign, AlertTriangle, Play, X } from 'lucide-react';
import { usePredictiveScalingData, PREDICTION_TYPES, TIME_HORIZONS } from '@/hooks/usePredictiveScalingData';
import { LoadingState } from '@/components/ui/loading-state';
import { useState } from 'react';

const PredictiveScalingPage = () => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { predictions, scalingActions, costAnalysis, accuracyMetrics, isLoading, generatePredictions, executeScalingAction, cancelScalingAction, getTotalSavings, getAverageAccuracy } = usePredictiveScalingData();
  const [selectedType, setSelectedType] = useState('concurrent_users');
  const [selectedHorizon, setSelectedHorizon] = useState('24h');

  if (isLoading) return <LoadingState message="Loading predictions..." />;

  const chartData = predictions.filter(p => p.prediction_type === selectedType).map(p => ({
    time: new Date(p.target_time).toLocaleTimeString(),
    predicted: p.predicted_value,
    lower: p.confidence_lower,
    upper: p.confidence_upper,
    actual: p.actual_value,
  }));

  const pendingActions = scalingActions.filter(a => a.status === 'pending');
  const avgAccuracy = getAverageAccuracy();

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Predictive Workload Scaling</h1>
          <p className="text-muted-foreground">AI-powered workload prediction and auto-scaling</p>
        </div>
        <div className="flex gap-2">
          <Select value={selectedType} onValueChange={setSelectedType}>
            <SelectTrigger className="w-48"><SelectValue /></SelectTrigger>
            <SelectContent>{PREDICTION_TYPES.map((t) => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent>
          </Select>
          <Select value={selectedHorizon} onValueChange={setSelectedHorizon}>
            <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
            <SelectContent>{TIME_HORIZONS.map((h) => <SelectItem key={h.value} value={h.value}>{h.label}</SelectItem>)}</SelectContent>
          </Select>
          <Button onClick={() => generatePredictions(selectedType, selectedHorizon)}><TrendingUp className="mr-2 h-4 w-4" />Generate</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Prediction Accuracy</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{avgAccuracy ? `${avgAccuracy.toFixed(1)}%` : 'N/A'}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Total Savings</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold text-green-500">${getTotalSavings().toFixed(2)}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Pending Actions</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold">{pendingActions.length}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm">Anomalies Detected</CardTitle></CardHeader>
          <CardContent><p className="text-2xl font-bold text-yellow-500">{predictions.filter(p => p.is_anomaly).length}</p></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workload Predictions</CardTitle>
          <CardDescription>Predicted vs actual load with confidence intervals</CardDescription>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="time" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip />
              <Area type="monotone" dataKey="upper" stroke="transparent" fill="hsl(var(--primary))" fillOpacity={0.1} />
              <Area type="monotone" dataKey="lower" stroke="transparent" fill="hsl(var(--background))" />
              <Line type="monotone" dataKey="predicted" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="actual" stroke="hsl(var(--chart-2))" strokeWidth={2} dot={false} strokeDasharray="5 5" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Proposed Scaling Actions</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {pendingActions.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">No pending actions</p>
            ) : pendingActions.map((action) => (
              <div key={action.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div>
                  <p className="font-medium">{action.action_type} {action.resource_type}</p>
                  <p className="text-sm text-muted-foreground">{action.previous_count} → {action.new_count} • {action.trigger_reason}</p>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => executeScalingAction(action.id)}><Play className="h-4 w-4" /></Button>
                  <Button size="sm" variant="outline" onClick={() => cancelScalingAction(action.id)}><X className="h-4 w-4" /></Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Cost Optimization</CardTitle></CardHeader>
          <CardContent className="space-y-2">
            {costAnalysis.slice(0, 5).map((cost) => (
              <div key={cost.id} className="flex items-center justify-between p-2 border rounded">
                <div>
                  <p className="font-medium">{cost.resource_type}</p>
                  <p className="text-xs text-muted-foreground">{new Date(cost.period_start).toLocaleDateString()}</p>
                </div>
                <div className="text-right">
                  <p className="text-green-500 font-medium">+${cost.savings?.toFixed(2) || 0}</p>
                  <p className="text-xs text-muted-foreground">ROI: {cost.roi?.toFixed(1) || 0}%</p>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PredictiveScalingPage;
