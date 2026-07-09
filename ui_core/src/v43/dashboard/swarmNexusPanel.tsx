import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { MetricCard } from "./OmegaShared";

export const SwarmNexusPanel = () => {
  const swarm = { nodeCount: "1,247", gpuEquivalent: "135" };
  return (
    <Card className="border-cyan-500">
      <CardHeader>
        <CardTitle className="text-cyan-600">
          [GLOBE] SWARM NEXUS -- The People's Cloud
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard 
            label="Active Nodes" 
            value={swarm.nodeCount}
            comparison="vs 1 datacenter"
            status="DISTRIBUTED"
          />
          <MetricCard 
            label="Virtual GPU Power" 
            value={`${swarm.gpuEquivalent} H100s`}
            comparison="From laptops and phones"
            status="EQUIVALENT"
          />
          <MetricCard 
            label="Cloud Cost" 
            value="$0.00"
            comparison="vs $25,000/month AWS"
            status="FREE"
          />
        </div>
      </CardContent>
    </Card>
  );
};
