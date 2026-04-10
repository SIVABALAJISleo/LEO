// Unknown Reality Handler
// Introduces explicit UNKNOWN_REALITY state for cases where automation must stop

export type RealityState = 
  | 'KNOWN'              // Fully understood, can automate
  | 'UNKNOWN_REALITY'    // Must freeze and require observation
  | 'PARTIALLY_KNOWN'    // Some aspects understood
  | 'EXPERIMENT_REQUIRED'; // Need controlled experiment

export interface UnknownRealityCase {
  caseId: string;
  category: string;
  description: string;
  
  // Discovery
  discoveredAt: string;
  discoveredBy: 'system' | 'user' | 'authority';
  
  // State
  state: RealityState;
  
  // Evidence
  observedSymptoms: string[];
  hypotheses: string[];
  
  // Resolution
  experimentRequired?: {
    description: string;
    expectedDuration: string;
    riskLevel: 'low' | 'medium' | 'high';
  };
  
  // Outcome
  resolvedAt?: string;
  resolution?: {
    newKnowledge: string;
    addedToKnowledgeBase: boolean;
    preventsFutureUnknowns: boolean;
  };
}

export interface KnowledgeEntry {
  entryId: string;
  category: string;
  knowledge: string;
  
  // Origin
  derivedFrom: string; // caseId of the unknown that led to this
  derivedAt: string;
  
  // Confidence
  confidence: number;
  validatedBy: string[];
}

export interface UnknownRealityStats {
  totalUnknowns: number;
  resolvedUnknowns: number;
  pendingUnknowns: number;
  averageResolutionTimeMs: number;
  knowledgeEntriesCreated: number;
}

class UnknownRealityHandler {
  private cases: Map<string, UnknownRealityCase> = new Map();
  private knowledgeBase: Map<string, KnowledgeEntry> = new Map();
  private stats: UnknownRealityStats = {
    totalUnknowns: 0,
    resolvedUnknowns: 0,
    pendingUnknowns: 0,
    averageResolutionTimeMs: 0,
    knowledgeEntriesCreated: 0
  };

  /**
   * Register a new unknown reality case - freezes automation
   */
  registerUnknown(params: {
    category: string;
    description: string;
    observedSymptoms: string[];
    hypotheses?: string[];
    discoveredBy?: 'system' | 'user' | 'authority';
  }): UnknownRealityCase {
    const caseId = `unknown_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const unknownCase: UnknownRealityCase = {
      caseId,
      category: params.category,
      description: params.description,
      discoveredAt: new Date().toISOString(),
      discoveredBy: params.discoveredBy || 'system',
      state: 'UNKNOWN_REALITY',
      observedSymptoms: params.observedSymptoms,
      hypotheses: params.hypotheses || []
    };

    this.cases.set(caseId, unknownCase);
    this.stats.totalUnknowns++;
    this.stats.pendingUnknowns++;

    console.log(`[UnknownReality] Registered unknown case ${caseId}: ${params.category}`);
    console.log(`[UnknownReality] AUTOMATION FROZEN for category: ${params.category}`);

    return unknownCase;
  }

  /**
   * Check if a category has any unresolved unknowns
   */
  hasUnresolvedUnknowns(category: string): boolean {
    return Array.from(this.cases.values())
      .some(c => c.category === category && c.state === 'UNKNOWN_REALITY');
  }

  /**
   * Get current reality state for a category
   */
  getRealityState(category: string): RealityState {
    const categoryCases = Array.from(this.cases.values())
      .filter(c => c.category === category);

    if (categoryCases.length === 0) {
      return 'KNOWN';
    }

    const hasUnknown = categoryCases.some(c => c.state === 'UNKNOWN_REALITY');
    const hasExperiment = categoryCases.some(c => c.state === 'EXPERIMENT_REQUIRED');
    const hasPartial = categoryCases.some(c => c.state === 'PARTIALLY_KNOWN');

    if (hasUnknown) return 'UNKNOWN_REALITY';
    if (hasExperiment) return 'EXPERIMENT_REQUIRED';
    if (hasPartial) return 'PARTIALLY_KNOWN';
    return 'KNOWN';
  }

  /**
   * Require an experiment to resolve an unknown
   */
  requireExperiment(caseId: string, experiment: {
    description: string;
    expectedDuration: string;
    riskLevel: 'low' | 'medium' | 'high';
  }): boolean {
    const unknownCase = this.cases.get(caseId);
    if (!unknownCase) return false;

    unknownCase.state = 'EXPERIMENT_REQUIRED';
    unknownCase.experimentRequired = experiment;

    console.log(`[UnknownReality] Experiment required for ${caseId}: ${experiment.description}`);
    return true;
  }

  /**
   * Submit observation/experiment results to resolve an unknown
   */
  submitObservation(caseId: string, observation: {
    result: string;
    confidence: number;
    validatedBy: string;
  }): {
    resolved: boolean;
    knowledgeEntry?: KnowledgeEntry;
  } {
    const unknownCase = this.cases.get(caseId);
    if (!unknownCase) {
      return { resolved: false };
    }

    // Create knowledge entry from observation
    const entryId = `knowledge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const entry: KnowledgeEntry = {
      entryId,
      category: unknownCase.category,
      knowledge: observation.result,
      derivedFrom: caseId,
      derivedAt: new Date().toISOString(),
      confidence: observation.confidence,
      validatedBy: [observation.validatedBy]
    };

    // Add to knowledge base
    this.knowledgeBase.set(entryId, entry);
    this.stats.knowledgeEntriesCreated++;

    // Resolve the unknown case
    unknownCase.state = 'KNOWN';
    unknownCase.resolvedAt = new Date().toISOString();
    unknownCase.resolution = {
      newKnowledge: observation.result,
      addedToKnowledgeBase: true,
      preventsFutureUnknowns: true
    };

    this.stats.resolvedUnknowns++;
    this.stats.pendingUnknowns--;

    // Update average resolution time
    const resolutionTimeMs = new Date(unknownCase.resolvedAt).getTime() - 
      new Date(unknownCase.discoveredAt).getTime();
    this.stats.averageResolutionTimeMs = 
      (this.stats.averageResolutionTimeMs * (this.stats.resolvedUnknowns - 1) + resolutionTimeMs) / 
      this.stats.resolvedUnknowns;

    console.log(`[UnknownReality] Case ${caseId} resolved. New knowledge added to base.`);
    console.log(`[UnknownReality] AUTOMATION RESUMED for category: ${unknownCase.category}`);

    return { resolved: true, knowledgeEntry: entry };
  }

  /**
   * Query knowledge base for a category
   */
  queryKnowledge(category: string): KnowledgeEntry[] {
    return Array.from(this.knowledgeBase.values())
      .filter(e => e.category === category)
      .sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Check if knowledge exists for a query
   */
  hasKnowledge(category: string, minConfidence: number = 0.8): boolean {
    return this.queryKnowledge(category)
      .some(e => e.confidence >= minConfidence);
  }

  /**
   * Get all pending unknown cases
   */
  getPendingCases(): UnknownRealityCase[] {
    return Array.from(this.cases.values())
      .filter(c => c.state === 'UNKNOWN_REALITY' || c.state === 'EXPERIMENT_REQUIRED');
  }

  /**
   * Get case by ID
   */
  getCase(caseId: string): UnknownRealityCase | undefined {
    return this.cases.get(caseId);
  }

  /**
   * Get statistics
   */
  getStats(): UnknownRealityStats {
    return { ...this.stats };
  }

  /**
   * Export knowledge base
   */
  exportKnowledgeBase(): KnowledgeEntry[] {
    return Array.from(this.knowledgeBase.values());
  }

  /**
   * Generate unknown reality report
   */
  generateReport(): {
    summary: string;
    pendingCases: UnknownRealityCase[];
    recentResolutions: UnknownRealityCase[];
    knowledgeGrowth: number;
  } {
    const pendingCases = this.getPendingCases();
    const recentResolutions = Array.from(this.cases.values())
      .filter(c => c.resolvedAt)
      .sort((a, b) => new Date(b.resolvedAt!).getTime() - new Date(a.resolvedAt!).getTime())
      .slice(0, 10);

    const summary = `
Unknown Reality Status:
- Total unknowns encountered: ${this.stats.totalUnknowns}
- Resolved: ${this.stats.resolvedUnknowns}
- Pending: ${this.stats.pendingUnknowns}
- Knowledge entries created: ${this.stats.knowledgeEntriesCreated}
- Avg resolution time: ${Math.round(this.stats.averageResolutionTimeMs / 1000)}s
    `.trim();

    return {
      summary,
      pendingCases,
      recentResolutions,
      knowledgeGrowth: this.stats.knowledgeEntriesCreated
    };
  }
}

export const unknownRealityHandler = new UnknownRealityHandler();
