import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Textarea } from "../../../components/ui/textarea";
import { Wand2 } from "lucide-react";
import { StatCard } from "./OmegaShared";

export const GenesisPanel = () => {
  return (
    <Card className="border-blue-500">
      <CardHeader>
        <CardTitle className="text-blue-600">
          [STAR] GENESIS ENGINE -- Speak, and It Shall Be Built
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <Textarea
            placeholder="Describe what you want to build..."
            className="min-h-[100px] bg-slate-900 border-slate-700 text-white"
          />
          <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
            <Wand2 className="mr-2 h-4 w-4" />
            Build with Genesis
          </Button>
          <div className="grid grid-cols-2 gap-4 mt-4">
            <StatCard label="Systems Built Today" value="1,247" />
            <StatCard label="CUDA Repos Migrated" value="23,456" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
