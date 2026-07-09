import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { MetricCard } from "./OmegaShared";

export const PhoenixPanel = () => {
  const phoenix = { vaccineCount: "15,420", strengthScore: "99.9" };
  return (
    <Card className="border-orange-500">
      <CardHeader>
        <CardTitle className="text-orange-600">
          [FIRE] PHOENIX RISING -- Stronger Every Crash
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard 
            label="Uptime" 
            value="100.00%"
            comparison="NVIDIA: 99.999%"
            status="SUPERIOR"
          />
          <MetricCard 
            label="Vaccines Applied" 
            value={phoenix.vaccineCount}
            comparison="Each failure makes system stronger"
            status="GROWING"
          />
          <MetricCard 
            label="System Strength" 
            value={`${phoenix.strengthScore}%`}
            comparison="Increases with every chaos event"
            status="ANTI-FRAGILE"
          />
        </div>
      </CardContent>
    </Card>
  );
};
