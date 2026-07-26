import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { MetricCard } from "./OmegaShared";

export const PerpetualMotionPanel = () => {
  const improvement = { patchCount: "2,341" };
  return (
    <Card className="border-emerald-500">
      <CardHeader>
        <CardTitle className="text-emerald-600">
          [SPIN] PERPETUAL MOTION -- Self-Improving Forever
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard
            label="Daily Improvement"
            value="1.2%"
            comparison="37x per year compound"
            status="ACCELERATING"
          />
          <MetricCard
            label="Auto-Patches"
            value={improvement.patchCount}
            comparison="Zero human intervention"
            status="AUTONOMOUS"
          />
          <MetricCard
            label="Innovation Source"
            value="Algorithms"
            comparison="NVIDIA: Physics-limited chips"
            status="UNBOUNDED"
          />
        </div>
      </CardContent>
    </Card>
  );
};
