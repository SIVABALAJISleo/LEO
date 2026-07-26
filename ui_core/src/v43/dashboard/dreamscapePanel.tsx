import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { MetricCard } from "./OmegaShared";

export const DreamscapePanel = () => {
  return (
    <Card className="border-pink-500">
      <CardHeader>
        <CardTitle className="text-pink-600">[ART] DREAMSCAPE -- Worlds, Not Pixels</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4">
          <MetricCard
            label="Image Gen Time"
            value="5s"
            comparison="vs 0.5s on H100"
            status="ACCEPTABLE"
          />
          <MetricCard
            label="Model Size"
            value="1B params"
            comparison="vs 50B on NVIDIA"
            status="TINY"
          />
          <MetricCard
            label="VRAM Needed"
            value="200MB"
            comparison="vs 24GB on RTX 4090"
            status="MINIMAL"
          />
        </div>
      </CardContent>
    </Card>
  );
};
