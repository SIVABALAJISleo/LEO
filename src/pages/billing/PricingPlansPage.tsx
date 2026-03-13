import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, Zap, Building2, Sparkles, Rocket } from 'lucide-react';
import { useBillingData, PLANS, PLAN_COMPARISON } from '@/hooks/useBillingData';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useState } from 'react';

const PricingPlansPage = () => {
  const { subscribe, currentPlan, isLoading } = useBillingData();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  const handlePlanAction = async (planId: string) => {
    if (planId === 'enterprise') {
      navigate('/billing/enterprise');
      return;
    }
    if (!user) {
      navigate('/auth/signup');
      return;
    }
    await subscribe(planId as 'free' | 'pro' | 'heavy');
  };

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'free': return <Zap className="h-6 w-6" />;
      case 'pro': return <Sparkles className="h-6 w-6" />;
      case 'heavy': return <Rocket className="h-6 w-6" />;
      case 'enterprise': return <Building2 className="h-6 w-6" />;
      default: return <Zap className="h-6 w-6" />;
    }
  };

  const formatPrice = (plan: typeof PLANS[0]) => {
    if (plan.price === null) return 'Custom';
    if (plan.price === 0) return '$0';
    
    const price = billingPeriod === 'yearly' && plan.yearlyPrice 
      ? plan.yearlyPrice 
      : plan.price;
    const priceMax = billingPeriod === 'yearly' && plan.yearlyPriceMax 
      ? plan.yearlyPriceMax 
      : plan.priceMax;
    
    if (priceMax && priceMax !== price) {
      return `$${price.toLocaleString('en-US')} – $${priceMax.toLocaleString('en-US')}`;
    }
    return `$${price.toLocaleString('en-US')}`;
  };

  return (
    <div className="space-y-8 p-6">
      <div className="text-center max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
        <p className="text-xl text-muted-foreground mb-6">
          RTX-5090-class outcomes through software-optimized execution.
        </p>
        
        {/* Billing Period Toggle */}
        <div className="inline-flex items-center gap-2 p-1 bg-muted rounded-lg">
          <Button 
            variant={billingPeriod === 'monthly' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setBillingPeriod('monthly')}
          >
            Monthly
          </Button>
          <Button 
            variant={billingPeriod === 'yearly' ? 'default' : 'ghost'}
            size="sm"
            onClick={() => setBillingPeriod('yearly')}
          >
            Yearly <Badge variant="secondary" className="ml-2">Save 20%</Badge>
          </Button>
        </div>
      </div>

      {/* Pricing Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 max-w-7xl mx-auto">
        {PLANS.map((plan) => (
          <Card 
            key={plan.id} 
            className={`relative flex flex-col ${plan.popular ? 'border-primary shadow-lg shadow-primary/20' : ''}`}
          >
            {plan.popular && (
              <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground">
                Most Popular
              </Badge>
            )}
            <CardHeader className="text-center pb-2">
              <div className="mx-auto mb-4 h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                {getPlanIcon(plan.id)}
              </div>
              <CardTitle className="text-2xl">{plan.name}</CardTitle>
              {plan.targetUsers && (
                <p className="text-xs text-muted-foreground">{plan.targetUsers}</p>
              )}
              <CardDescription>
                <span className="text-2xl font-bold text-foreground">
                  {formatPrice(plan)}
                </span>
                {plan.price !== null && (
                  <span className="text-base font-normal text-muted-foreground">
                    /{billingPeriod === 'yearly' ? 'year' : 'month'}
                  </span>
                )}
              </CardDescription>
              {plan.economics && (
                <p className="text-xs text-muted-foreground mt-2">{plan.economics}</p>
              )}
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              <ul className="space-y-3 mb-6 flex-1">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <Check className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button 
                className={`w-full ${plan.popular ? '' : 'variant-outline'}`}
                variant={plan.popular ? 'default' : 'outline'}
                onClick={() => handlePlanAction(plan.id)}
                disabled={isLoading || currentPlan === plan.id}
              >
                {currentPlan === plan.id ? 'Current Plan' : plan.cta}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Comparison Table */}
      <Card className="max-w-6xl mx-auto">
        <CardHeader>
          <CardTitle className="text-center">Compare Plans</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium">Feature</th>
                  <th className="text-center py-3 px-4 font-medium">Free</th>
                  <th className="text-center py-3 px-4 font-medium text-primary">HYPER Pro</th>
                  <th className="text-center py-3 px-4 font-medium">HYPER Heavy</th>
                  <th className="text-center py-3 px-4 font-medium">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {PLAN_COMPARISON.map((row, idx) => (
                  <tr key={idx} className="border-b last:border-0">
                    <td className="py-3 px-4 text-muted-foreground">{row.feature}</td>
                    <td className="text-center py-3 px-4">{row.free}</td>
                    <td className="text-center py-3 px-4 text-primary font-medium">{row.pro}</td>
                    <td className="text-center py-3 px-4">{row.heavy}</td>
                    <td className="text-center py-3 px-4">{row.enterprise}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Contact Sales */}
      <div className="text-center max-w-2xl mx-auto">
        <p className="text-muted-foreground">
          Need help choosing? <Button variant="link" onClick={() => navigate('/billing/enterprise')}>Contact our sales team</Button>
        </p>
      </div>
    </div>
  );
};

export default PricingPlansPage;
