import { useState, useMemo } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PerformanceMetric } from '@/lib/types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { format } from 'date-fns';

interface PerformanceTrendsChartProps {
  metrics: PerformanceMetric[];
}

type MetricType = 'latency' | 'throughput' | 'cache';

export const PerformanceTrendsChart = ({ metrics }: PerformanceTrendsChartProps) => {
  const [activeMetric, setActiveMetric] = useState<MetricType>('latency');

  const chartData = useMemo(() => {
    // Group metrics by hour
    const grouped: Record<string, { latency: number[]; throughput: number[]; cache: number[] }> = {};
    
    metrics.forEach((m) => {
      const hour = format(new Date(m.recorded_at), 'HH:00');
      if (!grouped[hour]) {
        grouped[hour] = { latency: [], throughput: [], cache: [] };
      }
      
      if (m.latency_ms || m.metric_name === 'latency') {
        grouped[hour].latency.push(m.latency_ms || m.metric_value || 0);
      }
      if (m.throughput_rps || m.metric_name === 'throughput') {
        grouped[hour].throughput.push(m.throughput_rps || m.metric_value || 0);
      }
      if (m.cache_hit_ratio || m.metric_name === 'cache_hit_ratio') {
        grouped[hour].cache.push((m.cache_hit_ratio || m.metric_value || 0) * 100);
      }
    });

    return Object.entries(grouped).map(([time, data]) => ({
      time,
      latency: data.latency.length > 0 
        ? data.latency.reduce((a, b) => a + b, 0) / data.latency.length 
        : null,
      throughput: data.throughput.length > 0 
        ? data.throughput.reduce((a, b) => a + b, 0) / data.throughput.length 
        : null,
      cache: data.cache.length > 0 
        ? data.cache.reduce((a, b) => a + b, 0) / data.cache.length 
        : null,
    }));
  }, [metrics]);

  const metricConfigs: Record<MetricType, { label: string; color: string; unit: string }> = {
    latency: { label: 'Latency', color: 'hsl(var(--primary))', unit: 'ms' },
    throughput: { label: 'Throughput', color: 'hsl(88, 72%, 60%)', unit: 'req/s' },
    cache: { label: 'Cache Hit', color: 'hsl(200, 72%, 50%)', unit: '%' },
  };

  const config = metricConfigs[activeMetric];

  return (
    <Card className="p-6 bg-card border-border">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Performance Trends (24h)</h3>
        <div className="flex gap-2">
          {(Object.keys(metricConfigs) as MetricType[]).map((key) => (
            <Button
              key={key}
              size="sm"
              variant={activeMetric === key ? 'default' : 'outline'}
              onClick={() => setActiveMetric(key)}
              className={activeMetric === key ? 'bg-gradient-primary' : ''}
            >
              {metricConfigs[key].label}
            </Button>
          ))}
        </div>
      </div>

      {chartData.length === 0 ? (
        <div className="h-[300px] flex items-center justify-center text-muted-foreground">
          <p>No performance data available</p>
        </div>
      ) : (
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="time"
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
              />
              <YAxis
                stroke="hsl(var(--muted-foreground))"
                fontSize={12}
                tickFormatter={(value) => `${value}${config.unit === '%' ? '%' : ''}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: 'hsl(var(--foreground))' }}
                formatter={(value: number) => [`${value.toFixed(2)} ${config.unit}`, config.label]}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey={activeMetric}
                name={config.label}
                stroke={config.color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6, fill: config.color }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
};
