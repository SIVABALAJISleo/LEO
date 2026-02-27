// Pre-Decision Compression Engine
// Compresses authority decisions to trivial confirmations by pre-computing safe outcomes

export type SafetyEnvelope = {
  safeActions: string[];
  unsafeActions: string[];
  recommendedAction: string;
  riskScore: number; // 0-1
  confidence: number; // 0-1
};

export type OutcomeSimulation = {
  scenarioId: string;
  description: string;
  probability: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  mitigationAvailable: boolean;
};

export type PreDecisionResult = {
  taskId: string;
  taskType: string;
  envelope: SafetyEnvelope;
  simulations: OutcomeSimulation[];
  singleSafeAction: boolean;
  explanation: string;
  evidence: string[];
  processingTimeMs: number;
  timestamp: string;
};

export type PreDecisionStats = {
  totalCompressions: number;
  singleActionRate: number;
  averageRiskReduction: number;
  averageProcessingMs: number;
};

class PreDecisionCompressor {
  private compressions: PreDecisionResult[] = [];
  private stats: PreDecisionStats = {
    totalCompressions: 0,
    singleActionRate: 0,
    averageRiskReduction: 0,
    averageProcessingMs: 0
  };

  async compress(
    taskId: string,
    taskType: string,
    possibleActions: string[],
    context: Record<string, unknown>
  ): Promise<PreDecisionResult> {
    const startTime = performance.now();

    // Simulate all possible outcomes
    const simulations = await this.simulateOutcomes(possibleActions, context);
    
    // Compute risk envelope
    const envelope = this.computeSafetyEnvelope(possibleActions, simulations);
    
    // Generate explanation and evidence
    const explanation = this.generateExplanation(envelope, simulations);
    const evidence = this.gatherEvidence(taskId, simulations, envelope);

    const processingTimeMs = performance.now() - startTime;

    const result: PreDecisionResult = {
      taskId,
      taskType,
      envelope,
      simulations,
      singleSafeAction: envelope.safeActions.length === 1,
      explanation,
      evidence,
      processingTimeMs,
      timestamp: new Date().toISOString()
    };

    this.recordCompression(result);
    return result;
  }

  private async simulateOutcomes(
    actions: string[],
    context: Record<string, unknown>
  ): Promise<OutcomeSimulation[]> {
    const simulations: OutcomeSimulation[] = [];

    for (const action of actions) {
      // Deterministic risk assessment based on action type
      const riskLevel = this.assessActionRisk(action, context);
      const probability = this.calculateProbability(action, context);
      
      simulations.push({
        scenarioId: `sim_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        description: `Outcome for action: ${action}`,
        probability,
        riskLevel,
        mitigationAvailable: riskLevel !== 'critical'
      });
    }

    return simulations;
  }

  private assessActionRisk(
    action: string,
    context: Record<string, unknown>
  ): 'low' | 'medium' | 'high' | 'critical' {
    const actionLower = action.toLowerCase();
    
    // Critical actions that require authority
    if (actionLower.includes('delete_all') || 
        actionLower.includes('terminate') ||
        actionLower.includes('irreversible')) {
      return 'critical';
    }
    
    // High risk actions
    if (actionLower.includes('modify_production') ||
        actionLower.includes('financial_transfer') ||
        actionLower.includes('access_sensitive')) {
      return 'high';
    }
    
    // Medium risk
    if (actionLower.includes('update') ||
        actionLower.includes('create') ||
        actionLower.includes('modify')) {
      return 'medium';
    }
    
    return 'low';
  }

  private calculateProbability(
    action: string,
    context: Record<string, unknown>
  ): number {
    // Base probability on historical patterns and context
    const hasHistory = context.historicalSuccess !== undefined;
    if (hasHistory) {
      return Math.min(0.99, Number(context.historicalSuccess) || 0.8);
    }
    return 0.85; // Default confidence for new actions
  }

  private computeSafetyEnvelope(
    actions: string[],
    simulations: OutcomeSimulation[]
  ): SafetyEnvelope {
    const safeActions: string[] = [];
    const unsafeActions: string[] = [];
    
    simulations.forEach((sim, index) => {
      if (sim.riskLevel === 'low' || (sim.riskLevel === 'medium' && sim.mitigationAvailable)) {
        safeActions.push(actions[index]);
      } else {
        unsafeActions.push(actions[index]);
      }
    });

    // Find best action among safe ones
    const recommendedAction = safeActions.length > 0 
      ? safeActions[0] 
      : 'REQUIRES_AUTHORITY_REVIEW';

    // Calculate overall risk score
    const riskScore = unsafeActions.length / actions.length;
    
    // Calculate confidence based on simulations
    const avgProbability = simulations.reduce((sum, s) => sum + s.probability, 0) / simulations.length;

    return {
      safeActions,
      unsafeActions,
      recommendedAction,
      riskScore,
      confidence: avgProbability
    };
  }

  private generateExplanation(
    envelope: SafetyEnvelope,
    simulations: OutcomeSimulation[]
  ): string {
    if (envelope.safeActions.length === 1) {
      return `Single safe action identified: "${envelope.recommendedAction}". All other options locked due to risk assessment. Confidence: ${(envelope.confidence * 100).toFixed(1)}%.`;
    }
    
    if (envelope.safeActions.length > 1) {
      return `${envelope.safeActions.length} safe actions available. Recommended: "${envelope.recommendedAction}". ${envelope.unsafeActions.length} options locked. Confidence: ${(envelope.confidence * 100).toFixed(1)}%.`;
    }
    
    return `All actions require authority review. Risk score: ${(envelope.riskScore * 100).toFixed(1)}%. Authority confirmation required before proceeding.`;
  }

  private gatherEvidence(
    taskId: string,
    simulations: OutcomeSimulation[],
    envelope: SafetyEnvelope
  ): string[] {
    const evidence: string[] = [
      `Task ID: ${taskId}`,
      `Timestamp: ${new Date().toISOString()}`,
      `Simulations run: ${simulations.length}`,
      `Safe actions: ${envelope.safeActions.length}`,
      `Unsafe actions locked: ${envelope.unsafeActions.length}`,
      `Recommended action: ${envelope.recommendedAction}`,
      `Risk score: ${envelope.riskScore.toFixed(4)}`,
      `Confidence: ${envelope.confidence.toFixed(4)}`
    ];

    // Add simulation details
    simulations.forEach((sim, i) => {
      evidence.push(`Scenario ${i + 1}: ${sim.riskLevel} risk, ${(sim.probability * 100).toFixed(1)}% probability`);
    });

    return evidence;
  }

  private recordCompression(result: PreDecisionResult): void {
    this.compressions.push(result);
    if (this.compressions.length > 1000) {
      this.compressions.shift();
    }

    // Update stats
    const total = this.compressions.length;
    const singleActionCount = this.compressions.filter(c => c.singleSafeAction).length;
    const avgRiskReduction = this.compressions.reduce((sum, c) => sum + (1 - c.envelope.riskScore), 0) / total;
    const avgProcessing = this.compressions.reduce((sum, c) => sum + c.processingTimeMs, 0) / total;

    this.stats = {
      totalCompressions: total,
      singleActionRate: singleActionCount / total,
      averageRiskReduction: avgRiskReduction,
      averageProcessingMs: avgProcessing
    };
  }

  getStats(): PreDecisionStats {
    return { ...this.stats };
  }

  getRecentCompressions(limit: number = 10): PreDecisionResult[] {
    return this.compressions.slice(-limit);
  }
}

export const preDecisionCompressor = new PreDecisionCompressor();
