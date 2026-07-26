import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Calculator, Cpu, HardDrive, Zap, Film } from "lucide-react";
import { calculateCost, PRICING_CONFIG } from "@/hooks/useBillingData";

const UsagePricingCalculatorPage = () => {
  const [usage, setUsage] = useState({
    inferenceTokens: 100000,
    trainingHours: 10,
    renderingHours: 5,
    storageGB: 25,
  });

  const costs = useMemo(() => calculateCost(usage), [usage]);
  const yearlyCost = costs.total * 12;

  const handleChange = (field: keyof typeof usage, value: string) => {
    const numValue = parseFloat(value) || 0;
    setUsage((prev) => ({ ...prev, [field]: numValue }));
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(amount);
  };

  return (
    <div className="space-y-8 p-6 max-w-4xl mx-auto">
      <div className="text-center">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-3 mb-2">
          <Calculator className="h-8 w-8 text-primary" />
          Usage Pricing Calculator
        </h1>
        <p className="text-muted-foreground">Estimate your monthly costs based on expected usage</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Input Card */}
        <Card>
          <CardHeader>
            <CardTitle>Your Usage</CardTitle>
            <CardDescription>Enter your estimated monthly usage</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Inference Tokens
              </Label>
              <Input
                type="number"
                value={usage.inferenceTokens}
                onChange={(e) => handleChange("inferenceTokens", e.target.value)}
                placeholder="e.g., 100000"
              />
              <p className="text-xs text-muted-foreground">
                Rate: ${PRICING_CONFIG.inference.rate} per{" "}
                {PRICING_CONFIG.inference.per.toLocaleString()} tokens
              </p>
            </div>

            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-primary" />
                Training Hours
              </Label>
              <Input
                type="number"
                value={usage.trainingHours}
                onChange={(e) => handleChange("trainingHours", e.target.value)}
                placeholder="e.g., 10"
              />
              <p className="text-xs text-muted-foreground">
                Rate: ${PRICING_CONFIG.training.rate} per hour
              </p>
            </div>

            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Film className="h-4 w-4 text-primary" />
                Rendering Hours
              </Label>
              <Input
                type="number"
                value={usage.renderingHours}
                onChange={(e) => handleChange("renderingHours", e.target.value)}
                placeholder="e.g., 5"
              />
              <p className="text-xs text-muted-foreground">
                Rate: ${PRICING_CONFIG.rendering.rate} per hour
              </p>
            </div>

            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <HardDrive className="h-4 w-4 text-primary" />
                Storage (GB)
              </Label>
              <Input
                type="number"
                value={usage.storageGB}
                onChange={(e) => handleChange("storageGB", e.target.value)}
                placeholder="e.g., 25"
              />
              <p className="text-xs text-muted-foreground">
                First {PRICING_CONFIG.storage.freeGB} GB free, then ${PRICING_CONFIG.storage.rate}
                /GB/month
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Cost Breakdown Card */}
        <Card className="bg-card">
          <CardHeader>
            <CardTitle>Cost Breakdown</CardTitle>
            <CardDescription>Estimated costs based on your usage</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <Zap className="h-4 w-4" /> Inference
                </span>
                <span className="font-medium">{formatCurrency(costs.inference)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <Cpu className="h-4 w-4" /> Training
                </span>
                <span className="font-medium">{formatCurrency(costs.training)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <Film className="h-4 w-4" /> Rendering
                </span>
                <span className="font-medium">{formatCurrency(costs.rendering)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2 text-muted-foreground">
                  <HardDrive className="h-4 w-4" /> Storage
                </span>
                <span className="font-medium">{formatCurrency(costs.storage)}</span>
              </div>
            </div>

            <Separator />

            <div className="space-y-3">
              <div className="flex justify-between items-center text-lg">
                <span className="font-semibold">Monthly Total</span>
                <span className="font-bold text-primary">{formatCurrency(costs.total)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Yearly Estimate</span>
                <span className="font-medium">{formatCurrency(yearlyCost)}</span>
              </div>
            </div>

            <Separator />

            <div className="bg-primary/10 rounded-lg p-4">
              <p className="text-sm text-center">
                <span className="font-medium">Tip:</span> Upgrade to HYPER Pro for priority
                processing and better rates on high-volume usage.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UsagePricingCalculatorPage;
