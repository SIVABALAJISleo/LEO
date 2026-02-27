import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from 'sonner';

export const PRICING_CONFIG = {
  inference: { rate: 0.001, per: 10000, unit: 'tokens' },
  training: { rate: 4.20, per: 1, unit: 'hour' },
  rendering: { rate: 2.40, per: 1, unit: 'hour' },
  storage: { freeGB: 10, rate: 0.01, per: 1, unit: 'GB/month' },
};

// RTX-5090 Value Anchor (internal reference): ~$660/month
// PRO: 10-15 users cover one RTX-5090-class cost
// HEAVY: 2-3 users cover one RTX-5090-class cost

export const PLANS = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    priceMax: 0,
    currency: '$',
    period: 'month',
    features: [
      'Basic dashboard access',
      'Up to 5 concurrent jobs',
      'Community support',
      '10 GB storage included',
      'Standard processing speed',
    ],
    cta: 'Get Started',
    popular: false,
  },
  {
    id: 'pro',
    name: 'HYPER Pro',
    price: 49,
    priceMax: 85,
    currency: '$',
    period: 'month',
    yearlyPrice: 490,
    yearlyPriceMax: 850,
    economics: 'Shared optimization · Non-deterministic routing',
    targetUsers: 'Developers · Creators · Indie teams',
    features: [
      'Optimized shared outcomes',
      'Up to 100 concurrent jobs',
      'Priority processing queue',
      'Advanced optimization modules',
      'Email support (24h response)',
      '500 GB storage included',
      'Full API access',
      'Symbolic compute engine',
    ],
    cta: 'Upgrade to Pro',
    popular: true,
  },
  {
    id: 'heavy',
    name: 'HYPER Heavy',
    price: 249,
    priceMax: 499,
    currency: '$',
    period: 'month',
    yearlyPrice: 2490,
    yearlyPriceMax: 4990,
    economics: 'Priority routing · Deterministic options · Compliance handling',
    targetUsers: 'AI teams · Studios · Research orgs',
    features: [
      'Priority outcome delivery',
      'Unlimited concurrent jobs',
      'Deterministic execution option',
      'Compliance & audit support',
      '24/7 priority support',
      'Custom integrations',
      'Dedicated account manager',
      'SLA guarantee (99.9%)',
      'Unlimited storage',
    ],
    cta: 'Get Heavy',
    popular: false,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: null,
    priceMax: null,
    currency: '$',
    period: 'month',
    features: [
      'Everything in Heavy',
      'On-premise deployment option',
      'Custom SLAs',
      'Dedicated infrastructure',
      'White-glove onboarding',
      'Volume discounts',
    ],
    cta: 'Contact Sales',
    popular: false,
  },
];

export const PLAN_COMPARISON = [
  { feature: 'Concurrent Jobs', free: '5', pro: '100', heavy: 'Unlimited', enterprise: 'Custom' },
  { feature: 'Storage', free: '10 GB', pro: '500 GB', heavy: 'Unlimited', enterprise: 'Custom' },
  { feature: 'Processing', free: 'Standard', pro: 'Priority Queue', heavy: 'Priority + Deterministic', enterprise: 'Dedicated' },
  { feature: 'Support', free: 'Community', pro: 'Email (24h)', heavy: '24/7 Priority', enterprise: 'White-glove' },
  { feature: 'Optimization Modules', free: 'Basic', pro: 'Advanced', heavy: 'Full Suite', enterprise: 'Custom' },
  { feature: 'API Access', free: '❌', pro: '✓', heavy: '✓', enterprise: '✓' },
  { feature: 'Deterministic Execution', free: '❌', pro: '❌', heavy: '✓', enterprise: '✓' },
  { feature: 'Compliance Support', free: '❌', pro: '❌', heavy: '✓', enterprise: '✓' },
  { feature: 'SLA', free: 'None', pro: 'None', heavy: '99.9%', enterprise: 'Custom' },
];

export function calculateCost(usage: {
  inferenceTokens: number;
  trainingHours: number;
  renderingHours: number;
  storageGB: number;
}) {
  const inferenceCost = (usage.inferenceTokens / PRICING_CONFIG.inference.per) * PRICING_CONFIG.inference.rate;
  const trainingCost = usage.trainingHours * PRICING_CONFIG.training.rate;
  const renderingCost = usage.renderingHours * PRICING_CONFIG.rendering.rate;
  const billableStorage = Math.max(0, usage.storageGB - PRICING_CONFIG.storage.freeGB);
  const storageCost = billableStorage * PRICING_CONFIG.storage.rate;

  return {
    inference: inferenceCost,
    training: trainingCost,
    rendering: renderingCost,
    storage: storageCost,
    total: inferenceCost + trainingCost + renderingCost + storageCost,
  };
}

interface BillingSubscription {
  id: string;
  user_id: string;
  plan: 'free' | 'pro' | 'heavy' | 'enterprise' | string; // Allow general string
  status: string;
  current_period_start?: string;
  current_period_end?: string;
  created_at: string;
}

interface BillingUsageRecord {
  id: string;
  month: string;
  inference_tokens: number | null;
  computed_cost: number | null;
  created_at: string;
}

export function useBillingData() {
  const { user } = useAuth();
  const [subscription, setSubscription] = useState<BillingSubscription | null>(null);
  const [usageRecords, setUsageRecords] = useState<BillingUsageRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user?.id) fetchBillingData();
  }, [user]);

  const fetchBillingData = async () => {
    if (!user?.id) return;
    setIsLoading(true);
    const [subRes, usageRes] = await Promise.all([
      supabase.from('billing_subscriptions').select('*').eq('user_id', user.id).order('created_at', { ascending: false }).limit(1),
      supabase.from('billing_usage_records').select('*').eq('user_id', user.id).order('month', { ascending: false }),
    ]);
    if (subRes.data && subRes.data.length > 0) {
      // Safe cast if shape roughly matches
      setSubscription(subRes.data[0] as unknown as BillingSubscription);
    }
    if (usageRes.data) {
      setUsageRecords(usageRes.data as unknown as BillingUsageRecord[]);
    }
    setIsLoading(false);
  };

  const subscribe = async (plan: 'free' | 'pro' | 'heavy' | 'enterprise') => {
    if (!user) return;

    if (plan === 'free') {
      // Free plan stays Supabase-only for simplicity
      const { data: existing } = await supabase
        .from('billing_subscriptions')
        .select('id')
        .eq('user_id', user.id)
        .limit(1);

      if (existing && existing.length > 0) {
        await supabase.from('billing_subscriptions').update({ plan, status: 'active' }).eq('id', existing[0].id);
      } else {
        await supabase.from('billing_subscriptions').insert({ user_id: user.id, plan, status: 'active' });
      }
      toast.success('Downgraded to Free plan');
      fetchBillingData();
      return;
    }

    try {
      // For paid plans, initiate Stripe Checkout via Backend
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/billing/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionStorage.getItem('firebase_token') || ''}`
        },
        body: JSON.stringify({ plan_id: plan })
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const { url } = await response.json();
      window.location.href = url; // Redirect to Stripe
    } catch (error) {
      console.error('Checkout error:', error);
      toast.error('Failed to initiate checkout. Please try again.');
    }
  };

  const recordUsage = async (usage: {
    inference_tokens: number;
    training_hours: number;
    rendering_hours: number;
    storage_gb: number;
  }) => {
    if (!user) return;
    const month = new Date().toISOString().slice(0, 7);
    const cost = calculateCost({
      inferenceTokens: usage.inference_tokens,
      trainingHours: usage.training_hours,
      renderingHours: usage.rendering_hours,
      storageGB: usage.storage_gb,
    });

    const { error } = await supabase.from('billing_usage_records').insert({
      user_id: user.id,
      month,
      ...usage,
      computed_cost: cost.total,
    });
    if (error) toast.error('Failed to record usage');
    else fetchBillingData();
  };

  const submitEnterpriseRequest = async (data: {
    name: string;
    email: string;
    company?: string;
    role?: string;
    expected_workload?: string;
    budget_range?: string;
    message?: string;
  }) => {
    if (!user) {
      toast.error('Please sign in to submit an enterprise quote request');
      return false;
    }

    const { error } = await supabase.from('enterprise_requests').insert({
      ...data,
      user_id: user.id,
    });
    if (error) {
      toast.error('Failed to submit request');
      return false;
    }
    toast.success('Quote request submitted – our team will contact you soon');
    return true;
  };

  return {
    subscription,
    usageRecords,
    isLoading,
    subscribe,
    recordUsage,
    submitEnterpriseRequest,
    currentPlan: subscription?.plan || 'free',
  };
}
