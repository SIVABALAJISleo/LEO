import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { LayerTrace } from "../../lib/api";

interface LayerWaterfallChartProps {
  data: LayerTrace[];
}

export const LayerWaterfallChart: React.FC<LayerWaterfallChartProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 w-full flex items-center justify-center text-muted-foreground bg-slate-50 dark:bg-slate-900 rounded-lg border border-dashed">
        Submit a query to view inference waterfall
      </div>
    );
  }

  // Add cumulative latency for waterfall effect
  let cumulative = 0;
  const chartData = data.map((d) => {
    const start = cumulative;
    cumulative += d.latency_ms;
    return {
      ...d,
      start,
      end: cumulative,
      duration: d.latency_ms,
    };
  });

  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 150, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
          <XAxis type="number" unit=" ms" />
          <YAxis type="category" dataKey="layer_name" width={180} tick={{ fontSize: 12 }} />
          <Tooltip
            cursor={{ fill: "rgba(255, 255, 255, 0.1)" }}
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const d = payload[0].payload;
                return (
                  <div className="bg-background border rounded-lg p-3 shadow-lg">
                    <p className="font-bold text-sm mb-1">{d.layer_name}</p>
                    <p className="text-xs text-muted-foreground">
                      Latency: <span className="text-foreground">{d.duration.toFixed(2)} ms</span>
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Confidence:{" "}
                      <span className="text-foreground">{(d.confidence * 100).toFixed(1)}%</span>
                    </p>
                    <p className="text-xs mt-1 font-medium">
                      Status:{" "}
                      {d.resolved ? (
                        <span className="text-green-500">RESOLVED</span>
                      ) : (
                        <span className="text-amber-500">BYPASSED</span>
                      )}
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          {/* Invisible bar to offset for waterfall */}
          <Bar dataKey="start" stackId="a" fill="transparent" />
          {/* Visible duration bar */}
          <Bar dataKey="duration" stackId="a" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.resolved ? "#10b981" : "#3b82f6"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
