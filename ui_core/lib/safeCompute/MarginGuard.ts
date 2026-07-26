/**
 * MarginGuard - Enforces minimum 40% gross margin under peak conditions
 *
 * If margin pressure occurs:
 * - Throttle acceptance
 * - Increase wait tolerance
 * - Restrict tier availability
 *
 * Never:
 * - Lower prices reactively
 * - Chase volume at loss
 */

export interface MarginPressureResponse {
  action: "accept" | "throttle" | "increase_wait" | "restrict_tier" | "defer";
  waitMultiplier: number;
  acceptanceRate: number;
  restrictedTiers: string[];
  reason: string;
}

export interface MarginMetrics {
  currentMargin: number;
  targetMargin: number;
  pressureLevel: "none" | "low" | "medium" | "high" | "critical";
  isHealthy: boolean;
}

class MarginGuardSystem {
  private readonly MIN_MARGIN = 0.4; // 40% minimum gross margin
  private readonly PRESSURE_THRESHOLDS = {
    low: 0.35,
    medium: 0.3,
    high: 0.25,
    critical: 0.2,
  };

  /**
   * Evaluate current margin and determine pressure response
   */
  evaluateMargin(
    revenue: number,
    costs: number,
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    pendingJobs: number,
  ): MarginPressureResponse {
    const margin = revenue > 0 ? (revenue - costs) / revenue : 1;
    const pressureLevel = this.getPressureLevel(margin);

    switch (pressureLevel) {
      case "critical":
        return {
          action: "restrict_tier",
          waitMultiplier: 3.0,
          acceptanceRate: 0.25,
          restrictedTiers: ["free", "pro"],
          reason: "Critical margin pressure - restricting to enterprise only",
        };

      case "high":
        return {
          action: "throttle",
          waitMultiplier: 2.0,
          acceptanceRate: 0.5,
          restrictedTiers: ["free"],
          reason: "High margin pressure - throttling free tier",
        };

      case "medium":
        return {
          action: "increase_wait",
          waitMultiplier: 1.5,
          acceptanceRate: 0.75,
          restrictedTiers: [],
          reason: "Medium margin pressure - increasing wait tolerance",
        };

      case "low":
        return {
          action: "defer",
          waitMultiplier: 1.2,
          acceptanceRate: 0.9,
          restrictedTiers: [],
          reason: "Low margin pressure - deferring non-priority jobs",
        };

      default:
        return {
          action: "accept",
          waitMultiplier: 1.0,
          acceptanceRate: 1.0,
          restrictedTiers: [],
          reason: "Healthy margin - accepting all jobs",
        };
    }
  }

  /**
   * Get current margin metrics
   */
  getMetrics(revenue: number, costs: number): MarginMetrics {
    const margin = revenue > 0 ? (revenue - costs) / revenue : 1;
    const pressureLevel = this.getPressureLevel(margin);

    return {
      currentMargin: margin,
      targetMargin: this.MIN_MARGIN,
      pressureLevel,
      isHealthy: margin >= this.MIN_MARGIN,
    };
  }

  /**
   * Check if a pricing decision should be blocked
   */
  shouldBlockPricing(
    proposedRevenue: number,
    expectedCost: number,
  ): {
    blocked: boolean;
    reason?: string;
  } {
    const margin = (proposedRevenue - expectedCost) / proposedRevenue;

    if (margin < this.PRESSURE_THRESHOLDS.critical) {
      return {
        blocked: true,
        reason: "Would result in critically low margin",
      };
    }

    if (margin < this.MIN_MARGIN) {
      return {
        blocked: true,
        reason: `Margin ${(margin * 100).toFixed(1)}% below minimum ${this.MIN_MARGIN * 100}%`,
      };
    }

    return { blocked: false };
  }

  private getPressureLevel(margin: number): MarginMetrics["pressureLevel"] {
    if (margin >= this.MIN_MARGIN) return "none";
    if (margin >= this.PRESSURE_THRESHOLDS.low) return "low";
    if (margin >= this.PRESSURE_THRESHOLDS.medium) return "medium";
    if (margin >= this.PRESSURE_THRESHOLDS.high) return "high";
    return "critical";
  }
}

export const marginGuard = new MarginGuardSystem();
