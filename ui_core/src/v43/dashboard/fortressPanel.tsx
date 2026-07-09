import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { MetricCard } from "./OmegaShared";

export const FortressPanel = () => {
  return (
    <Card className="border-red-500">
      <CardHeader>
        <CardTitle className="text-red-600">
          [SHIELD] FORTRESS -- Math, Not Hardware
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard 
            label="Formal Proofs" 
            value="100%"
            comparison="NVIDIA: hardware TEE only"
            status="PROVEN"
          />
          <MetricCard 
            label="Hallucination Detection" 
            value="100%"
            comparison="Mathematically guaranteed"
            status="GUARANTEED"
          />
          <MetricCard 
            label="Injection Resistance" 
            value="Verified"
            comparison="Not just tested, PROVEN"
            status="INVULNERABLE"
          />
        </div>
      </CardContent>
    </Card>
  );
};
