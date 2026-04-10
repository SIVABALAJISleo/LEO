/**
 * PricingEngine - RTX-5090 value-anchored pricing system
 * 
 * Internal reference: RTX-5090-class system ≈ $660/month
 * (hardware amortization + power + cooling + ops + software + networking)
 * 
 * This is a pricing anchor, not a hardware claim.
 */

export interface PricingTier {
  id: string;
  name: string;
  monthlyMin: number;
  monthlyMax: number;
  yearlyMin: number;
  yearlyMax: number;
  currency: string;
  economics: string;
  targetUsers: string;
  usersPerRTX5090: string;
  features: string[];
  restrictions: string[];
}

export interface MarginStatus {
  currentMargin: number;
  minRequired: number;
  isHealthy: boolean;
  action: 'accept' | 'throttle' | 'restrict' | 'defer';
}

class PricingEngineSystem {
  // Internal anchor - RTX-5090-class monthly cost
  private readonly RTX5090_MONTHLY_COST = 660; // $660
  private readonly MIN_GROSS_MARGIN = 0.40; // 40% minimum
  
  private readonly FORBIDDEN_CLAIMS = [
    'dedicated gpu',
    'unlimited compute',
    'replacing cloud gpus',
    'cost-per-hour gpu'
  ];
  
  private readonly ALLOWED_CLAIM = 'RTX-5090-class outcomes through software-optimized execution.';

  /**
   * Official pricing tiers - USD
   */
  readonly tiers: Record<string, PricingTier> = {
    pro: {
      id: 'pro',
      name: 'HYPER Pro',
      monthlyMin: 49,
      monthlyMax: 85,
      yearlyMin: 490, // ~2 months free
      yearlyMax: 850,
      currency: '$',
      economics: 'Shared optimization · Non-deterministic routing · No SLA',
      targetUsers: 'Developers · Creators · Indie teams',
      usersPerRTX5090: '10-15 PRO users cover one RTX-5090-class cost',
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
      restrictions: [
        'No SLA guarantee',
        'Non-deterministic routing',
        'Shared resource pool'
      ]
    },
    heavy: {
      id: 'heavy',
      name: 'HYPER Heavy',
      monthlyMin: 249,
      monthlyMax: 499,
      yearlyMin: 2490,
      yearlyMax: 4990,
      currency: '$',
      economics: 'Priority routing · Deterministic options · Compliance handling',
      targetUsers: 'AI teams · Studios · Research orgs',
      usersPerRTX5090: '2-3 HEAVY users cover one RTX-5090-class cost',
      features: [
        'Priority outcome delivery',
        'Unlimited concurrent jobs',
        'Deterministic execution option',
        'Compliance & audit support',
        '24/7 priority support',
        'Custom integrations',
        'Dedicated account manager',
        'On-premise deployment option',
        'Unlimited storage',
        'SLA guarantee (99.9%)',
      ],
      restrictions: []
    }
  };

  /**
   * Check if a claim is allowed
   */
  isClaimAllowed(claim: string): boolean {
    const lowerClaim = claim.toLowerCase();
    return !this.FORBIDDEN_CLAIMS.some(forbidden => 
      lowerClaim.includes(forbidden)
    );
  }

  /**
   * Get the only allowed phrasing
   */
  getAllowedClaim(): string {
    return this.ALLOWED_CLAIM;
  }

  /**
   * Calculate margin status
   */
  calculateMarginStatus(
    revenue: number,
    costs: number
  ): MarginStatus {
    const margin = revenue > 0 ? (revenue - costs) / revenue : 0;
    const isHealthy = margin >= this.MIN_GROSS_MARGIN;

    let action: MarginStatus['action'] = 'accept';
    if (!isHealthy) {
      if (margin < 0.20) {
        action = 'restrict';
      } else if (margin < 0.30) {
        action = 'throttle';
      } else {
        action = 'defer';
      }
    }

    return {
      currentMargin: margin,
      minRequired: this.MIN_GROSS_MARGIN,
      isHealthy,
      action
    };
  }

  /**
   * Get tier pricing for display
   */
  getTierPricing(tierId: 'pro' | 'heavy'): {
    monthly: { min: number; max: number };
    yearly: { min: number; max: number };
    currency: string;
  } {
    const tier = this.tiers[tierId];
    return {
      monthly: { min: tier.monthlyMin, max: tier.monthlyMax },
      yearly: { min: tier.yearlyMin, max: tier.yearlyMax },
      currency: tier.currency
    };
  }

  /**
   * Validate pricing decision against margin requirements
   */
  validatePricingDecision(
    selectedPrice: number,
    estimatedCost: number
  ): { valid: boolean; reason?: string } {
    const margin = (selectedPrice - estimatedCost) / selectedPrice;
    
    if (margin < this.MIN_GROSS_MARGIN) {
      return {
        valid: false,
        reason: `Margin ${(margin * 100).toFixed(1)}% below minimum ${this.MIN_GROSS_MARGIN * 100}%`
      };
    }
    
    return { valid: true };
  }

  /**
   * Internal reference only - never expose
   */
  getInternalAnchor(): { rtx5090Monthly: number; minMargin: number } {
    return {
      rtx5090Monthly: this.RTX5090_MONTHLY_COST,
      minMargin: this.MIN_GROSS_MARGIN
    };
  }
}

export const pricingEngine = new PricingEngineSystem();
