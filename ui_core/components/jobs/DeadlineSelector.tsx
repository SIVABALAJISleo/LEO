// DeadlineSelector - Allows users to set deadlines and see alternatives
// Part of deadline-aware scheduling system

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Clock, Zap, Sparkles, Server, AlertCircle, CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import {
  deadlineScheduler,
  type DeadlineEstimate,
  type QualityLevel,
} from "@/lib/safeCompute/DeadlineScheduler";

export interface DeadlineSelectorProps {
  jobTier: string;
  memoryMb?: number;
  onSelect: (quality: QualityLevel, deadlineMs?: number) => void;
  className?: string;
}

const PRESET_DEADLINES = [
  { label: "ASAP", ms: 5000 },
  { label: "1 min", ms: 60000 },
  { label: "5 min", ms: 300000 },
  { label: "30 min", ms: 1800000 },
  { label: "No rush", ms: 3600000 },
];

const QUALITY_ICONS = {
  approximate: <Zap className="h-4 w-4 text-amber-500" />,
  reduced: <Sparkles className="h-4 w-4 text-blue-500" />,
  full: <Server className="h-4 w-4 text-green-500" />,
};

export function DeadlineSelector({
  jobTier,
  memoryMb,
  onSelect,
  className,
}: DeadlineSelectorProps) {
  const [selectedDeadline, setSelectedDeadline] = useState(PRESET_DEADLINES[2].ms);
  const [estimate, setEstimate] = useState<DeadlineEstimate | null>(null);
  const [selectedQuality, setSelectedQuality] = useState<QualityLevel>("full");

  // Update estimate when deadline or tier changes
  useEffect(() => {
    const newEstimate = deadlineScheduler.estimateDeadline(jobTier, selectedDeadline, memoryMb);
    setEstimate(newEstimate);
    setSelectedQuality(newEstimate.recommendation);
  }, [selectedDeadline, jobTier, memoryMb]);

  const handleDeadlineChange = (value: number[]) => {
    setSelectedDeadline(value[0]);
  };

  const handleSubmit = () => {
    onSelect(selectedQuality, selectedDeadline);
  };

  if (!estimate) return null;

  const timeRange = deadlineScheduler.getTimeRange(estimate.estimatedCompletionTime);

  return (
    <Card className={cn("border-border", className)}>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Clock className="h-4 w-4 text-primary" />
          When do you need this?
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Deadline Presets */}
        <div className="flex flex-wrap gap-2">
          {PRESET_DEADLINES.map((preset) => (
            <Button
              key={preset.ms}
              variant={selectedDeadline === preset.ms ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedDeadline(preset.ms)}
              className="text-xs"
            >
              {preset.label}
            </Button>
          ))}
        </div>

        {/* Custom Slider */}
        <div className="space-y-2">
          <Slider
            value={[selectedDeadline]}
            onValueChange={handleDeadlineChange}
            min={5000}
            max={3600000}
            step={5000}
            className="py-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Instant</span>
            <span>1 hour</span>
          </div>
        </div>

        {/* Feasibility Status */}
        <div
          className={cn(
            "flex items-center gap-2 p-3 rounded-lg text-sm",
            estimate.canMeetDeadline
              ? "bg-green-500/10 text-green-600"
              : "bg-amber-500/10 text-amber-600",
          )}
        >
          {estimate.canMeetDeadline ? (
            <>
              <CheckCircle2 className="h-4 w-4" />
              <span>Full quality available within your timeframe</span>
            </>
          ) : (
            <>
              <AlertCircle className="h-4 w-4" />
              <span>
                Full quality needs more time ({timeRange.min} – {timeRange.max})
              </span>
            </>
          )}
        </div>

        {/* Quality Options */}
        <RadioGroup
          value={selectedQuality}
          onValueChange={(v) => setSelectedQuality(v as QualityLevel)}
          className="space-y-2"
        >
          {estimate.alternatives
            .filter((a) => a.available)
            .map((alt) => (
              <div
                key={alt.id}
                className={cn(
                  "flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors",
                  selectedQuality === alt.quality
                    ? "border-primary bg-primary/5"
                    : "border-border hover:bg-muted/30",
                )}
                onClick={() => setSelectedQuality(alt.quality)}
              >
                <RadioGroupItem value={alt.quality} id={alt.id} />
                <div className="flex-1">
                  <Label htmlFor={alt.id} className="flex items-center gap-2 cursor-pointer">
                    {QUALITY_ICONS[alt.quality]}
                    <span className="font-medium">{alt.label}</span>
                    {alt.quality === estimate.recommendation && (
                      <Badge variant="secondary" className="text-xs ml-2">
                        Recommended
                      </Badge>
                    )}
                  </Label>
                  <p className="text-xs text-muted-foreground mt-0.5">{alt.description}</p>
                </div>
                <div className="text-right text-xs text-muted-foreground">
                  <p>{deadlineScheduler.formatTimeEstimate(alt.estimatedTime)}</p>
                  <p>
                    {Math.round(alt.confidenceRange[0] * 100)}–
                    {Math.round(alt.confidenceRange[1] * 100)}%
                  </p>
                </div>
              </div>
            ))}
        </RadioGroup>

        {/* Submit Button */}
        <Button onClick={handleSubmit} className="w-full">
          Continue with{" "}
          {selectedQuality === "approximate"
            ? "Quick"
            : selectedQuality === "reduced"
              ? "Balanced"
              : "Full"}{" "}
          Quality
        </Button>
      </CardContent>
    </Card>
  );
}
