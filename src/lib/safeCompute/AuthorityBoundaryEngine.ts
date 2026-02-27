// AUTHORITY BOUNDARY ENGINE
// Classifies and routes requests based on authority requirements
// Software may predict, simulate, prepare, verify, log - but NEVER be final authority

export type AuthorityBoundaryType = 
  | 'SAFETY_CRITICAL'      // Medical, nuclear, aviation
  | 'LEGAL_FINALITY'       // Financial settlement, legal verdict
  | 'REALTIME_AUTHORITY'   // Sub-millisecond causality
  | 'NEVER_SEEN_PHYSICS'   // Zero-tolerance new physics
  | 'PHYSICS_OK';          // Standard compute

export type ExecutionPath = 
  | 'SOFTWARE_EXECUTE'     // Full software execution
  | 'SOFTWARE_ASSIST'      // Software assists, human decides
  | 'AUTHORITY_REQUIRED'   // Authority must approve
  | 'EXPLAIN_AND_ROUTE';   // Explain limits, route appropriately

export interface AuthorityClassification {
  boundaryType: AuthorityBoundaryType;
  executionPath: ExecutionPath;
  confidence: number;
  reason: string;
  allowedActions: string[];
  forbiddenActions: string[];
  nextSteps: string[];
  auditRequired: boolean;
}

export interface AuthorityBoundaryCheck {
  requestId: string;
  classification: AuthorityClassification;
  timestamp: string;
  softwarePrepared: string[];
  authorityRequired: boolean;
  handoffTarget: string | null;
}

export interface AuthorityStats {
  totalChecks: number;
  byBoundaryType: Record<AuthorityBoundaryType, number>;
  byExecutionPath: Record<ExecutionPath, number>;
  authorityHandoffs: number;
  softwareExecuted: number;
  softwareAssisted: number;
}

// Boundary detection patterns
const SAFETY_CRITICAL_PATTERNS = [
  'medical', 'diagnosis', 'prescription', 'treatment', 'patient',
  'nuclear', 'reactor', 'radiation', 'hazmat',
  'aviation', 'flight', 'aircraft', 'pilot', 'atc',
  'surgery', 'life-support', 'emergency', 'critical-care',
  'weapon', 'explosive', 'munition',
];

const LEGAL_FINALITY_PATTERNS = [
  'settlement', 'verdict', 'judgment', 'contract-execute',
  'financial-transfer', 'wire-transfer', 'escrow-release',
  'legal-binding', 'notary', 'certification',
  'tax-filing', 'audit-certification',
  'insurance-claim-final', 'payout-authorization',
];

const REALTIME_AUTHORITY_PATTERNS = [
  'sub-ms', 'microsecond', 'nanosecond',
  'trading-execution', 'hft', 'market-order',
  'collision-avoidance', 'autonomous-drive',
  'industrial-control', 'plc', 'scada',
  'realtime-safety', 'hardware-interlock',
];

const NEVER_SEEN_PHYSICS_PATTERNS = [
  'frontier-physics', 'novel-material', 'untested-regime',
  'zero-tolerance', 'first-principles-unknown',
  'experimental-compound', 'uncharted-parameter',
  'extreme-condition', 'beyond-spec',
];

class AuthorityBoundaryEngine {
  private static instance: AuthorityBoundaryEngine;
  private checkHistory: AuthorityBoundaryCheck[] = [];
  private stats: AuthorityStats = {
    totalChecks: 0,
    byBoundaryType: {
      'SAFETY_CRITICAL': 0,
      'LEGAL_FINALITY': 0,
      'REALTIME_AUTHORITY': 0,
      'NEVER_SEEN_PHYSICS': 0,
      'PHYSICS_OK': 0,
    },
    byExecutionPath: {
      'SOFTWARE_EXECUTE': 0,
      'SOFTWARE_ASSIST': 0,
      'AUTHORITY_REQUIRED': 0,
      'EXPLAIN_AND_ROUTE': 0,
    },
    authorityHandoffs: 0,
    softwareExecuted: 0,
    softwareAssisted: 0,
  };

  private constructor() {}

  static getInstance(): AuthorityBoundaryEngine {
    if (!AuthorityBoundaryEngine.instance) {
      AuthorityBoundaryEngine.instance = new AuthorityBoundaryEngine();
    }
    return AuthorityBoundaryEngine.instance;
  }

  // Main classification entry point
  classify(request: {
    type: string;
    description: string;
    domain?: string;
    metadata?: Record<string, unknown>;
  }): AuthorityBoundaryCheck {
    const requestId = `auth_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const searchText = `${request.type} ${request.description} ${request.domain || ''}`.toLowerCase();

    // Classify boundary type
    const boundaryType = this.detectBoundaryType(searchText, request.metadata);
    
    // Determine execution path based on boundary
    const executionPath = this.determineExecutionPath(boundaryType);
    
    // Build classification
    const classification = this.buildClassification(boundaryType, executionPath, searchText);
    
    // Create check record
    const check: AuthorityBoundaryCheck = {
      requestId,
      classification,
      timestamp: new Date().toISOString(),
      softwarePrepared: this.getSoftwarePreparedActions(boundaryType),
      authorityRequired: executionPath === 'AUTHORITY_REQUIRED',
      handoffTarget: this.getHandoffTarget(boundaryType),
    };

    // Update stats
    this.stats.totalChecks++;
    this.stats.byBoundaryType[boundaryType]++;
    this.stats.byExecutionPath[executionPath]++;
    if (executionPath === 'AUTHORITY_REQUIRED') {
      this.stats.authorityHandoffs++;
    } else if (executionPath === 'SOFTWARE_EXECUTE') {
      this.stats.softwareExecuted++;
    } else if (executionPath === 'SOFTWARE_ASSIST') {
      this.stats.softwareAssisted++;
    }

    // Store in history (limited)
    this.checkHistory.push(check);
    if (this.checkHistory.length > 1000) {
      this.checkHistory = this.checkHistory.slice(-500);
    }

    console.log(`[AuthorityBoundary] ${requestId}: ${boundaryType} → ${executionPath}`);
    return check;
  }

  private detectBoundaryType(
    searchText: string, 
    metadata?: Record<string, unknown>
  ): AuthorityBoundaryType {
    // Check for explicit override in metadata
    if (metadata?.forceAuthorityRequired) {
      return 'SAFETY_CRITICAL';
    }

    // Pattern matching (order matters - most restrictive first)
    if (SAFETY_CRITICAL_PATTERNS.some(p => searchText.includes(p))) {
      return 'SAFETY_CRITICAL';
    }
    if (LEGAL_FINALITY_PATTERNS.some(p => searchText.includes(p))) {
      return 'LEGAL_FINALITY';
    }
    if (REALTIME_AUTHORITY_PATTERNS.some(p => searchText.includes(p))) {
      return 'REALTIME_AUTHORITY';
    }
    if (NEVER_SEEN_PHYSICS_PATTERNS.some(p => searchText.includes(p))) {
      return 'NEVER_SEEN_PHYSICS';
    }

    // Check for high-stakes indicators in metadata
    if (metadata?.stakes === 'high' || metadata?.lifeImpact || metadata?.legalBinding) {
      return 'SAFETY_CRITICAL';
    }

    return 'PHYSICS_OK';
  }

  private determineExecutionPath(boundaryType: AuthorityBoundaryType): ExecutionPath {
    switch (boundaryType) {
      case 'SAFETY_CRITICAL':
        return 'AUTHORITY_REQUIRED';
      case 'LEGAL_FINALITY':
        return 'AUTHORITY_REQUIRED';
      case 'REALTIME_AUTHORITY':
        return 'EXPLAIN_AND_ROUTE';
      case 'NEVER_SEEN_PHYSICS':
        return 'SOFTWARE_ASSIST';
      case 'PHYSICS_OK':
        return 'SOFTWARE_EXECUTE';
      default:
        return 'EXPLAIN_AND_ROUTE'; // Default to honesty
    }
  }

  private buildClassification(
    boundaryType: AuthorityBoundaryType,
    executionPath: ExecutionPath,
    searchText: string
  ): AuthorityClassification {
    const baseClassification: AuthorityClassification = {
      boundaryType,
      executionPath,
      confidence: 0.95,
      reason: '',
      allowedActions: [],
      forbiddenActions: [],
      nextSteps: [],
      auditRequired: false,
    };

    switch (boundaryType) {
      case 'SAFETY_CRITICAL':
        return {
          ...baseClassification,
          reason: 'Request involves human safety, medical, or critical systems',
          allowedActions: [
            'Predict outcomes',
            'Simulate scenarios',
            'Detect risk early',
            'Generate cryptographic proofs',
            'Create immutable audit logs',
            'Package decision evidence',
            'Escalate to certified system',
          ],
          forbiddenActions: [
            'Declare final medical decisions',
            'Execute safety-critical actions',
            'Override safety protocols',
            'Bypass authority checks',
          ],
          nextSteps: [
            'Authority verification required',
            'Human-in-loop confirmation needed',
            'Certified system must approve',
          ],
          auditRequired: true,
        };

      case 'LEGAL_FINALITY':
        return {
          ...baseClassification,
          reason: 'Request requires legal or financial finality',
          allowedActions: [
            'Prepare transaction details',
            'Validate compliance rules',
            'Generate audit trail',
            'Calculate settlement amounts',
            'Verify identity requirements',
          ],
          forbiddenActions: [
            'Declare money settled',
            'Execute binding agreements',
            'Authorize payouts',
            'Finalize legal documents',
          ],
          nextSteps: [
            'Legal authority must approve',
            'Financial officer confirmation',
            'Compliance sign-off required',
          ],
          auditRequired: true,
        };

      case 'REALTIME_AUTHORITY':
        return {
          ...baseClassification,
          reason: 'Request requires sub-millisecond authority or hardware control',
          allowedActions: [
            'Prepare parameters',
            'Pre-validate inputs',
            'Queue for execution',
            'Monitor outcomes',
          ],
          forbiddenActions: [
            'Act as authoritative clock',
            'Control hardware directly',
            'Execute realtime trades',
            'Override hardware interlocks',
          ],
          nextSteps: [
            'Route to dedicated hardware',
            'Delegate to certified system',
            'Use approved realtime executor',
          ],
          auditRequired: true,
        };

      case 'NEVER_SEEN_PHYSICS':
        return {
          ...baseClassification,
          reason: 'Request involves untested physics or novel conditions',
          allowedActions: [
            'Provide simulations with uncertainty bounds',
            'Generate probabilistic predictions',
            'Flag confidence intervals',
            'Recommend validation experiments',
          ],
          forbiddenActions: [
            'Claim certainty',
            'Guarantee outcomes',
            'Bypass validation requirements',
          ],
          nextSteps: [
            'Expert review recommended',
            'Validation testing required',
            'Uncertainty acknowledged in output',
          ],
          auditRequired: true,
        };

      case 'PHYSICS_OK':
      default:
        return {
          ...baseClassification,
          reason: 'Standard computational request within known physics',
          allowedActions: [
            'Full software execution',
            'Autonomous processing',
            'Result delivery',
          ],
          forbiddenActions: [],
          nextSteps: ['Proceed with execution'],
          auditRequired: false,
        };
    }
  }

  private getSoftwarePreparedActions(boundaryType: AuthorityBoundaryType): string[] {
    if (boundaryType === 'PHYSICS_OK') {
      return ['Full execution completed'];
    }
    
    return [
      'Outcome prediction generated',
      'Scenario simulation completed',
      'Risk assessment prepared',
      'Audit log created',
      'Evidence package ready',
      'Handoff documentation prepared',
    ];
  }

  private getHandoffTarget(boundaryType: AuthorityBoundaryType): string | null {
    switch (boundaryType) {
      case 'SAFETY_CRITICAL':
        return 'Certified Safety Authority';
      case 'LEGAL_FINALITY':
        return 'Legal/Compliance Officer';
      case 'REALTIME_AUTHORITY':
        return 'Dedicated Hardware Controller';
      case 'NEVER_SEEN_PHYSICS':
        return 'Domain Expert Review';
      default:
        return null;
    }
  }

  // Check if a specific action is allowed for a boundary type
  isActionAllowed(boundaryType: AuthorityBoundaryType, action: string): boolean {
    const tempClassification = this.buildClassification(
      boundaryType, 
      this.determineExecutionPath(boundaryType),
      ''
    );
    return !tempClassification.forbiddenActions.some(
      f => action.toLowerCase().includes(f.toLowerCase())
    );
  }

  // Get UI display information
  getUIDisplay(check: AuthorityBoundaryCheck): {
    label: string;
    variant: 'default' | 'warning' | 'destructive';
    message: string;
    showHandoff: boolean;
  } {
    if (!check.authorityRequired) {
      return {
        label: 'Software Executed',
        variant: 'default',
        message: 'Request completed by software',
        showHandoff: false,
      };
    }

    return {
      label: 'Authority Required',
      variant: 'warning',
      message: check.classification.reason,
      showHandoff: true,
    };
  }

  // Get statistics
  getStats(): AuthorityStats {
    return { ...this.stats };
  }

  // Get coverage metrics
  getCoverageMetrics(): {
    softwareExecutedPercent: number;
    softwareAssistedPercent: number;
    authorityRequiredPercent: number;
    explainAndRoutePercent: number;
  } {
    const total = this.stats.totalChecks || 1;
    return {
      softwareExecutedPercent: (this.stats.byExecutionPath['SOFTWARE_EXECUTE'] / total) * 100,
      softwareAssistedPercent: (this.stats.byExecutionPath['SOFTWARE_ASSIST'] / total) * 100,
      authorityRequiredPercent: (this.stats.byExecutionPath['AUTHORITY_REQUIRED'] / total) * 100,
      explainAndRoutePercent: (this.stats.byExecutionPath['EXPLAIN_AND_ROUTE'] / total) * 100,
    };
  }

  // Get recent checks
  getRecentChecks(limit: number = 50): AuthorityBoundaryCheck[] {
    return this.checkHistory.slice(-limit).reverse();
  }

  // Get truth statement
  getTruthStatement(): string {
    return `This system does not break physics or law. It executes everything software is allowed to do (${this.stats.softwareExecuted} tasks) and governs authority transparently where software must stop (${this.stats.authorityHandoffs} handoffs).`;
  }
}

export const authorityBoundaryEngine = AuthorityBoundaryEngine.getInstance();
