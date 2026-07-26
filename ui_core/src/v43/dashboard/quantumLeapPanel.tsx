import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { MetricCard } from "./OmegaShared";

export const QuantumLeapPanel = () => {
  return (
    <Card className="border-indigo-500">
      <CardHeader>
        <CardTitle className="text-indigo-600">
          [ATOM] QUANTUM LEAP -- Infinite Scale via Time
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard
            label="Max Task Size"
            value="Infinite"
            comparison="Limited only by time, not hardware"
            status="UNBOUNDED"
          />
          <MetricCard
            label="Queue Depth"
            value="1,000,000+"
            comparison="Tasks processed when compute available"
            status="SCALABLE"
          />
          <MetricCard
            label="Cost per Task"
            value="$0.0001"
            comparison="vs $0.02 on cloud GPU"
            status="NEAR-ZERO"
          />
        </div>
      </CardContent>
    </Card>
  );
};
