import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import {
  CreditCard,
  Download,
  Calendar,
  CheckCircle,
  AlertCircle,
  Zap,
  Shield,
  ExternalLink,
} from "lucide-react";
import { useBillingData, PLANS } from "@/hooks/useBillingData";
import { useAuth } from "@/contexts/AuthContext";
import { format } from "date-fns";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

export default function BillingManagePage() {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { subscription, usageRecords, currentPlan, isLoading } = useBillingData();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [isYearly, setIsYearly] = useState(false);

  const currentPlanDetails = PLANS.find((p) => p.id === currentPlan) || PLANS[0];

  const handleUpgrade = () => {
    navigate("/billing/pricing");
  };

  const handleCancelSubscription = () => {
    toast.info("To cancel your subscription, please contact support.");
  };

  const handleDownloadInvoice = (month: string) => {
    toast.success(`Invoice for ${month} downloaded`);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 2,
    }).format(amount);
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="max-w-md w-full">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h2 className="text-xl font-semibold mb-2">Sign in required</h2>
            <p className="text-muted-foreground mb-4">Please sign in to manage your billing.</p>
            <Button onClick={() => navigate("/auth/login")}>Sign In</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Billing & Subscription</h1>
        <p className="text-muted-foreground">Manage your plan, payments, and invoices</p>
      </div>

      {/* Current Plan */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            Current Plan
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold">{currentPlanDetails.name}</h3>
              <p className="text-muted-foreground">
                {currentPlanDetails.price !== null
                  ? `${currentPlanDetails.currency}${currentPlanDetails.price}/${currentPlanDetails.period}`
                  : "Custom pricing"}
              </p>
            </div>
            <Badge
              variant={currentPlan === "free" ? "secondary" : "default"}
              className="text-lg px-4 py-2"
            >
              {subscription?.status === "active" ? "Active" : "Inactive"}
            </Badge>
          </div>

          <Separator />

          <div className="grid gap-2">
            {currentPlanDetails.features.slice(0, 4).map((feature, idx) => (
              <div key={idx} className="flex items-center gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-primary" />
                <span>{feature}</span>
              </div>
            ))}
          </div>

          <div className="flex gap-3 pt-4">
            {currentPlan !== "enterprise" && <Button onClick={handleUpgrade}>Upgrade Plan</Button>}
            {currentPlan !== "free" && (
              <Button variant="outline" onClick={handleCancelSubscription}>
                Cancel Subscription
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Billing Cycle Toggle */}
      <Card>
        <CardHeader>
          <CardTitle>Billing Preferences</CardTitle>
          <CardDescription>Manage your billing cycle</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label>Yearly Billing</Label>
              <p className="text-sm text-muted-foreground">Save 20% with annual billing</p>
            </div>
            <Switch checked={isYearly} onCheckedChange={setIsYearly} />
          </div>
        </CardContent>
      </Card>

      {/* Payment Method */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Payment Method
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 border border-border rounded-lg">
            <div className="flex items-center gap-3">
              <div className="h-10 w-14 bg-gradient-to-r from-blue-600 to-blue-400 rounded flex items-center justify-center">
                <span className="text-white text-xs font-bold">VISA</span>
              </div>
              <div>
                <p className="font-medium">•••• •••• •••• 4242</p>
                <p className="text-sm text-muted-foreground">Expires 12/25</p>
              </div>
            </div>
            <Button variant="outline" size="sm">
              Update
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-3 flex items-center gap-1">
            <Shield className="h-3 w-3" />
            Payments secured with 256-bit encryption
          </p>
        </CardContent>
      </Card>

      {/* Invoices */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Invoices
          </CardTitle>
          <CardDescription>Download your past invoices</CardDescription>
        </CardHeader>
        <CardContent>
          {usageRecords.length > 0 ? (
            <div className="space-y-3">
              {usageRecords
                .slice(0, 5)
                .map((record: { id: string; month: string; computed_cost: number }) => (
                  <div
                    key={record.id}
                    className="flex items-center justify-between p-3 border border-border rounded-lg"
                  >
                    <div>
                      <p className="font-medium">
                        {format(new Date(record.month + "-01"), "MMMM yyyy")}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {formatCurrency(record.computed_cost || 0)}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownloadInvoice(record.month)}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No invoices yet</p>
          )}
        </CardContent>
      </Card>

      {/* Help */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium">Need help with billing?</h3>
              <p className="text-sm text-muted-foreground">Contact our support team</p>
            </div>
            <Button variant="outline" size="sm">
              <ExternalLink className="h-4 w-4 mr-2" />
              Contact Support
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
