import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";

export const FreeEnergyPanel = () => {
  return (
    <Card className="border-yellow-500">
      <CardHeader>
        <CardTitle className="text-yellow-600">
          [ENERGY] FREE ENERGY -- Zero Marginal Cost
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8">
          <p className="text-6xl font-bold text-green-600">$0.00</p>
          <p className="text-xl text-gray-500 mt-2">
            Total Cost of Ownership (5 years)
          </p>
          <p className="text-sm text-gray-400 mt-1">
            vs $190,000 for NVIDIA DGX
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
