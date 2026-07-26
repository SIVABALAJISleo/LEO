// HYPER System Boundary - Domain and scope limits

type WorkloadOrigin = "hyper-app" | "hyper-api" | "partner-pipeline" | "external" | "unknown";

interface BoundaryCheck {
  allowed: boolean;
  origin: WorkloadOrigin;
  reason?: string;
}

// INTERNAL RULES - Never exposed to UI
const SCOPE_RULES = {
  // HYPER does NOT own global users
  // HYPER reduces global GPU work indirectly
  // "Serve" ≠ "Compute" ≠ "Replace hardware"

  allowedOrigins: ["hyper-app", "hyper-api", "partner-pipeline"] as WorkloadOrigin[],

  // Never optimize these (outside HYPER domain)
  blockedDomains: [
    "os-gpu", // OS-level GPU usage
    "gaming", // Games
    "video-streaming", // Video streaming platforms
    "system-ui", // System UI
    "background-process", // Background processes
  ],
};

class SystemBoundaryEngine {
  private static instance: SystemBoundaryEngine;
  private partnerPipelines: Set<string> = new Set();

  private constructor() {}

  static getInstance(): SystemBoundaryEngine {
    if (!SystemBoundaryEngine.instance) {
      SystemBoundaryEngine.instance = new SystemBoundaryEngine();
    }
    return SystemBoundaryEngine.instance;
  }

  // Check if workload is within HYPER's domain
  checkBoundary(origin: WorkloadOrigin, domain?: string): BoundaryCheck {
    // Block external origins
    if (!SCOPE_RULES.allowedOrigins.includes(origin)) {
      return {
        allowed: false,
        origin,
        reason: "Outside HYPER optimization scope",
      };
    }

    // Block restricted domains
    if (domain && SCOPE_RULES.blockedDomains.includes(domain)) {
      return {
        allowed: false,
        origin,
        reason: "Domain outside optimization scope",
      };
    }

    return {
      allowed: true,
      origin,
    };
  }

  // Register a partner pipeline
  registerPartner(partnerId: string): void {
    this.partnerPipelines.add(partnerId);
  }

  // Check if a partner is registered
  isPartner(partnerId: string): boolean {
    return this.partnerPipelines.has(partnerId);
  }

  // Determine origin from request context
  determineOrigin(context: {
    source?: string;
    apiKey?: string;
    partnerId?: string;
  }): WorkloadOrigin {
    if (context.partnerId && this.isPartner(context.partnerId)) {
      return "partner-pipeline";
    }
    if (context.apiKey) {
      return "hyper-api";
    }
    if (context.source === "app") {
      return "hyper-app";
    }
    return "unknown";
  }

  // Get allowed claims for public messaging (firewall)
  getAllowedClaims(): string[] {
    return [
      "HYPER reduces redundant GPU computation through software.",
      "Intelligent workload optimization.",
      "Efficient compute resource management.",
    ];
  }

  // Get forbidden claims (never use these)
  getForbiddenClaims(): string[] {
    return [
      "Serving billions of users",
      "Replacing global GPUs",
      "Cloud-scale compute on a laptop",
      "Infinite scale",
      "Zero-wait heavy compute",
    ];
  }
}

export const systemBoundary = SystemBoundaryEngine.getInstance();
export type { BoundaryCheck, WorkloadOrigin };
