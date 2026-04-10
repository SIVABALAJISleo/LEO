// AUTHORITY-MINIMIZATION ROUTER
// Core intelligence layer that scores and routes every task
// Maximizes software-handled coverage while preserving all boundaries

import { digitalTwinVerifier, type DigitalTwinResult } from './DigitalTwinVerifier';
import { cryptographicProofPipeline, type ExecutionProof } from './CryptographicProofPipeline';
import { predictiveCausalityBuffer, type CausalPrediction } from './PredictiveCausalityBuffer';
import { physicsSurrogateEngine, type SurrogatePrediction } from './PhysicsSurrogateEngine';
import { authorityBoundaryEngine, type AuthorityBoundaryCheck } from './AuthorityBoundaryEngine';

export type AuthorityDecision = 'SOFTWARE_ONLY' | 'SOFTWARE_ASSISTED' | 'AUTHORITY_REQUIRED';

export interface TaskScore {
  safetyScore: number;      // 0-1: Higher = more safety-critical
  legalityScore: number;    // 0-1: Higher = more legally binding
  timingScore: number;      // 0-1: Higher = more time-sensitive
  noveltyScore: number;     // 0-1: Higher = more novel/uncertain
  overallRisk: number;      // 0-1: Composite risk score
}

export interface AuthorityRoutingResult {
  taskId: string;
  decision: AuthorityDecision;
  scores: TaskScore;
  twinResult?: DigitalTwinResult;
  proof?: ExecutionProof;
  prediction?: CausalPrediction;
  surrogateResult?: SurrogatePrediction;
  boundaryCheck: AuthorityBoundaryCheck;
  escalationReason: string | null;
  evidencePrepared: string[];
  processingTimeMs: number;
  timestamp: string;
}

export interface AuthorityMinimizationStats {
  totalRoutings: number;
  softwareOnlyCount: number;
  softwareAssistedCount: number;
  authorityRequiredCount: number;
  escalationsAvoided: number;
  decisionsAccelerated: number;
  autoApprovals: number;
  proofsGenerated: number;
  avgProcessingTimeMs: number;
}

export interface AuthorityMinimizationMetrics {
  softwareHandledPercent: number;
  authorityRequiredPercent: number;
  escalationAvoidanceRate: number;
  decisionAccelerationRate: number;
  autoApprovalRate: number;
}

// Decision thresholds
const SOFTWARE_ONLY_THRESHOLD = 0.20;
const SOFTWARE_ASSISTED_THRESHOLD = 0.60;

class AuthorityMinimizationRouter {
  private static instance: AuthorityMinimizationRouter;
  private routingHistory: AuthorityRoutingResult[] = [];
  private stats: AuthorityMinimizationStats = {
    totalRoutings: 0,
    softwareOnlyCount: 0,
    softwareAssistedCount: 0,
    authorityRequiredCount: 0,
    escalationsAvoided: 0,
    decisionsAccelerated: 0,
    autoApprovals: 0,
    proofsGenerated: 0,
    avgProcessingTimeMs: 0,
  };

  private constructor() {}

  static getInstance(): AuthorityMinimizationRouter {
    if (!AuthorityMinimizationRouter.instance) {
      AuthorityMinimizationRouter.instance = new AuthorityMinimizationRouter();
    }
    return AuthorityMinimizationRouter.instance;
  }

  // Main routing entry point
  async route(params: {
    taskId: string;
    taskType: string;
    description: string;
    context: Record<string, unknown>;
    domain?: string;
    inputParameters?: Record<string, number>;
  }): Promise<AuthorityRoutingResult> {
    const startTime = Date.now();
    const evidencePrepared: string[] = [];

    // Step 1: Score the task
    const scores = this.scoreTask(params.taskType, params.description, params.context);

    // Step 2: Get authority boundary classification
    const boundaryCheck = authorityBoundaryEngine.classify({
      type: params.taskType,
      description: params.description,
      domain: params.domain,
      metadata: params.context,
    });

    // Step 3: Initialize results
    let twinResult: DigitalTwinResult | undefined;
    let proof: ExecutionProof | undefined;
    let prediction: CausalPrediction | undefined;
    let surrogateResult: SurrogatePrediction | undefined;

    // Step 4: Apply authority-minimization techniques based on initial classification
    if (boundaryCheck.authorityRequired || scores.overallRisk > SOFTWARE_ONLY_THRESHOLD) {
      
      // Try Digital Twin + Formal Verification to reduce escalation
      twinResult = await digitalTwinVerifier.simulateAction({
        actionId: params.taskId,
        actionType: params.taskType,
        context: params.context,
      });
      evidencePrepared.push('Digital twin simulation completed');
      evidencePrepared.push(`Formal verification: ${twinResult.constraintCheckPassed ? 'PASSED' : 'FAILED'}`);

      // If twin recommends auto-approval, we may reduce authority requirement
      if (twinResult.autoApprovalRecommended && !boundaryCheck.authorityRequired) {
        this.stats.escalationsAvoided++;
        this.stats.autoApprovals++;
      }
    }

    // Step 5: Generate cryptographic proof for audit trail
    // eslint-disable-next-line prefer-const
    proof = await cryptographicProofPipeline.generateProof({
      type: 'decision',
      input: { taskId: params.taskId, type: params.taskType, scores },
      output: { boundaryCheck: boundaryCheck.classification, twinResult: twinResult?.overallConfidence },
      executionContext: params.context,
    });
    evidencePrepared.push(`Cryptographic proof generated: ${proof.proofId}`);
    this.stats.proofsGenerated++;

    // Step 6: Use predictive causality if applicable
    if (params.context.requiresRealtime) {
      prediction = predictiveCausalityBuffer.predict({
        actionType: params.taskType,
        currentState: params.context.currentState,
        actionParams: params.context as Record<string, unknown>,
      });
      evidencePrepared.push(`Causal prediction: ${prediction.confidence} confidence`);
    }

    // Step 7: Use physics surrogate if applicable
    if (params.domain && params.inputParameters && 
        physicsSurrogateEngine.getAvailableSurrogates().includes(params.domain)) {
      surrogateResult = physicsSurrogateEngine.predict({
        domain: params.domain,
        inputParameters: params.inputParameters,
      });
      evidencePrepared.push(`Physics surrogate: ${surrogateResult.uncertaintyLevel} uncertainty`);
    }

    // Step 8: Make final routing decision
    let decision: AuthorityDecision;
    let escalationReason: string | null = null;

    if (boundaryCheck.authorityRequired) {
      // Hard boundary - must escalate
      decision = 'AUTHORITY_REQUIRED';
      escalationReason = boundaryCheck.classification.reason;
    } else if (twinResult?.autoApprovalRecommended && scores.overallRisk <= SOFTWARE_ONLY_THRESHOLD) {
      // Twin approved and low risk - software only
      decision = 'SOFTWARE_ONLY';
      this.stats.decisionsAccelerated++;
    } else if (scores.overallRisk <= SOFTWARE_ONLY_THRESHOLD) {
      // Low risk - software only
      decision = 'SOFTWARE_ONLY';
    } else if (scores.overallRisk <= SOFTWARE_ASSISTED_THRESHOLD) {
      // Medium risk - software assisted
      decision = 'SOFTWARE_ASSISTED';
      if (twinResult && !twinResult.escalationRequired) {
        this.stats.escalationsAvoided++;
      }
    } else {
      // High risk - authority required
      decision = 'AUTHORITY_REQUIRED';
      escalationReason = `Risk score ${(scores.overallRisk * 100).toFixed(1)}% exceeds threshold`;
      if (twinResult?.escalationRequired) {
        escalationReason = twinResult.escalationReason || escalationReason;
      }
    }

    const result: AuthorityRoutingResult = {
      taskId: params.taskId,
      decision,
      scores,
      twinResult,
      proof,
      prediction,
      surrogateResult,
      boundaryCheck,
      escalationReason,
      evidencePrepared,
      processingTimeMs: Date.now() - startTime,
      timestamp: new Date().toISOString(),
    };

    // Update stats
    this.stats.totalRoutings++;
    switch (decision) {
      case 'SOFTWARE_ONLY':
        this.stats.softwareOnlyCount++;
        break;
      case 'SOFTWARE_ASSISTED':
        this.stats.softwareAssistedCount++;
        break;
      case 'AUTHORITY_REQUIRED':
        this.stats.authorityRequiredCount++;
        break;
    }
    this.stats.avgProcessingTimeMs = (
      (this.stats.avgProcessingTimeMs * (this.stats.totalRoutings - 1) + result.processingTimeMs) /
      this.stats.totalRoutings
    );

    // Store in history
    this.routingHistory.push(result);
    if (this.routingHistory.length > 1000) {
      this.routingHistory = this.routingHistory.slice(-500);
    }

    console.log(`[AuthorityRouter] ${params.taskId}: ${decision}, risk: ${(scores.overallRisk * 100).toFixed(1)}%`);
    return result;
  }

  private scoreTask(
    taskType: string,
    description: string,
    context: Record<string, unknown>
  ): TaskScore {
    const searchText = `${taskType} ${description}`.toLowerCase();

    // Safety scoring
    let safetyScore = 0.10; // Base safety score
    const safetyKeywords = ['medical', 'health', 'safety', 'critical', 'emergency', 'life'];
    if (safetyKeywords.some(k => searchText.includes(k))) {
      safetyScore = 0.90;
    } else if (context.affectsUsers || context.production) {
      safetyScore = 0.40;
    }

    // Legality scoring
    let legalityScore = 0.10;
    const legalKeywords = ['payment', 'contract', 'settlement', 'legal', 'compliance', 'audit'];
    if (legalKeywords.some(k => searchText.includes(k))) {
      legalityScore = 0.85;
    } else if (context.involvesFinance || context.requiresCompliance) {
      legalityScore = 0.50;
    }

    // Timing scoring
    let timingScore = 0.10;
    const timingKeywords = ['realtime', 'instant', 'immediate', 'urgent', 'microsecond'];
    if (timingKeywords.some(k => searchText.includes(k))) {
      timingScore = 0.80;
    } else if (context.timeConstraintMs && (context.timeConstraintMs as number) < 100) {
      timingScore = 0.60;
    }

    // Novelty scoring
    let noveltyScore = 0.10;
    const noveltyKeywords = ['experimental', 'novel', 'untested', 'frontier', 'unknown'];
    if (noveltyKeywords.some(k => searchText.includes(k))) {
      noveltyScore = 0.70;
    } else if (context.isExperimental || context.noPrecedent) {
      noveltyScore = 0.50;
    }

    // Composite risk score (weighted average)
    const overallRisk = (
      safetyScore * 0.35 +
      legalityScore * 0.30 +
      timingScore * 0.15 +
      noveltyScore * 0.20
    );

    return {
      safetyScore,
      legalityScore,
      timingScore,
      noveltyScore,
      overallRisk,
    };
  }

  // Quick route for simple tasks
  quickRoute(taskType: string): AuthorityDecision {
    const lowRiskTypes = ['read', 'list', 'search', 'query', 'validate', 'preview'];
    const highRiskTypes = ['delete', 'payment', 'transfer', 'admin', 'medical', 'legal'];

    if (lowRiskTypes.some(t => taskType.toLowerCase().includes(t))) {
      return 'SOFTWARE_ONLY';
    }
    if (highRiskTypes.some(t => taskType.toLowerCase().includes(t))) {
      return 'AUTHORITY_REQUIRED';
    }
    return 'SOFTWARE_ASSISTED';
  }

  // Get statistics
  getStats(): AuthorityMinimizationStats {
    return { ...this.stats };
  }

  // Get coverage metrics
  getMetrics(): AuthorityMinimizationMetrics {
    const total = this.stats.totalRoutings || 1;
    const softwareHandled = this.stats.softwareOnlyCount + this.stats.softwareAssistedCount;
    
    return {
      softwareHandledPercent: (softwareHandled / total) * 100,
      authorityRequiredPercent: (this.stats.authorityRequiredCount / total) * 100,
      escalationAvoidanceRate: (this.stats.escalationsAvoided / total) * 100,
      decisionAccelerationRate: (this.stats.decisionsAccelerated / total) * 100,
      autoApprovalRate: (this.stats.autoApprovals / total) * 100,
    };
  }

  // Get target vs actual coverage
  getCoverageReport(): {
    target: { softwareHandled: string; authorityRequired: string };
    actual: { softwareHandled: string; authorityRequired: string };
    onTarget: boolean;
  } {
    const metrics = this.getMetrics();
    const targetSoftware = 99.7;
    const targetAuthority = 0.3;

    return {
      target: { 
        softwareHandled: `${targetSoftware}%`, 
        authorityRequired: `${targetAuthority}%` 
      },
      actual: { 
        softwareHandled: `${metrics.softwareHandledPercent.toFixed(2)}%`, 
        authorityRequired: `${metrics.authorityRequiredPercent.toFixed(2)}%` 
      },
      onTarget: metrics.softwareHandledPercent >= targetSoftware - 0.5,
    };
  }

  // Get recent routings
  getRecentRoutings(limit: number = 20): AuthorityRoutingResult[] {
    return this.routingHistory.slice(-limit).reverse();
  }

  // Get routing by task ID
  getRouting(taskId: string): AuthorityRoutingResult | undefined {
    return this.routingHistory.find(r => r.taskId === taskId);
  }

  // Get aggregate report for dashboard
  getAggregateReport(): {
    stats: AuthorityMinimizationStats;
    metrics: AuthorityMinimizationMetrics;
    coverageReport: ReturnType<typeof this.getCoverageReport>;
    componentStats: {
      digitalTwin: ReturnType<typeof digitalTwinVerifier.getStats>;
      cryptoProof: ReturnType<typeof cryptographicProofPipeline.getStats>;
      causality: ReturnType<typeof predictiveCausalityBuffer.getStats>;
      surrogate: ReturnType<typeof physicsSurrogateEngine.getStats>;
      authority: ReturnType<typeof authorityBoundaryEngine.getStats>;
    };
  } {
    return {
      stats: this.getStats(),
      metrics: this.getMetrics(),
      coverageReport: this.getCoverageReport(),
      componentStats: {
        digitalTwin: digitalTwinVerifier.getStats(),
        cryptoProof: cryptographicProofPipeline.getStats(),
        causality: predictiveCausalityBuffer.getStats(),
        surrogate: physicsSurrogateEngine.getStats(),
        authority: authorityBoundaryEngine.getStats(),
      },
    };
  }

  // Get truth statement
  getTruthStatement(): string {
    const metrics = this.getMetrics();
    return `Authority-Minimization Router: ${this.stats.totalRoutings} tasks routed. ` +
           `Software-handled: ${metrics.softwareHandledPercent.toFixed(2)}%, ` +
           `Authority-required: ${metrics.authorityRequiredPercent.toFixed(2)}% (explicit). ` +
           `Escalations avoided: ${this.stats.escalationsAvoided}, ` +
           `Decisions accelerated: ${this.stats.decisionsAccelerated}. ` +
           `All boundaries preserved with cryptographic proof.`;
  }
}

export const authorityMinimizationRouter = AuthorityMinimizationRouter.getInstance();
