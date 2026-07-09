import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Alert, AlertTitle, AlertDescription } from "../../../components/ui/alert";
import { MetricCard, StatCard } from "./OmegaShared";

export const HiveMindPanel = () => {
  const swarm = { totalFLOPS: "4.2", gpuEquivalent: "135" };
  return (
    <Card className="border-purple-500">
      <CardHeader>
        <CardTitle className="text-purple-600">
          [HIVE] HIVE MIND -- Humanity Trains the Model
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="font-bold text-white">Swarm Compute</h3>
            <p className="text-2xl text-purple-400">{swarm.totalFLOPS} PFLOPS</p>
            <p className="text-sm text-gray-500">
              Equivalent to {swarm.gpuEquivalent} H100s
            </p>
          </div>
          <div>
            <h3 className="font-bold text-white">Training Cost</h3>
            <p className="text-2xl text-purple-400">$0.00</p>
            <p className="text-sm text-gray-500">
              vs $40,000 for NVIDIA DGX
            </p>
          </div>
        </div>
        <Alert className="mt-4 bg-purple-50">
          <AlertTitle>Why This Beats NVIDIA</AlertTitle>
          <AlertDescription>
            NVIDIA trains on $40M GPU clusters. You train on 1,000 laptops 
            that people already own. The intelligence is the same. 
            The cost is zero. The scalability is infinite.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
};
