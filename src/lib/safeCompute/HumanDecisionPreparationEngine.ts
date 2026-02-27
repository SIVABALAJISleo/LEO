/**
 * Human Decision Preparation Engine
 * 
 * Prepares humans for authority decisions by:
 * - Collecting all relevant data
 * - Analyzing patterns
 * - Predicting outcomes
 * - Showing risks, confidence, uncertainty
 * - Generating clear recommendations
 * - Providing one-click approve/reject interface
 * 
 * NEVER replaces human authority - only prepares them.
 */

export type DecisionCategory = 
  | 'financial'
  | 'legal'
  | 'medical'
  | 'safety'
  | 'operational'
  | 'strategic';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface DataPoint {
  source: string;
  value: unknown;
  timestamp: number;
  reliability: number; // 0-1
}

export interface Pattern {
  id: string;
  name: string;
  frequency: number;
  confidence: number;
  relevance: number;
}

export interface PredictedOutcome {
  id: string;
  description: string;
  probability: number;
  impact: 'positive' | 'negative' | 'neutral';
  magnitude: number; // 1-10
  timeframe: string;
}

export interface RiskAssessment {
  level: RiskLevel;
  factors: string[];
  mitigations: string[];
  residualRisk: number; // 0-1
}

export interface DecisionRecommendation {
  action: 'approve' | 'reject' | 'defer' | 'escalate';
  confidence: number;
  reasoning: string[];
  alternatives: string[];
  warnings: string[];
}

export interface PreparedDecision {
  id: string;
  category: DecisionCategory;
  title: string;
  summary: string;
  
  // Data collection
  dataPoints: DataPoint[];
  dataCompleteness: number; // 0-1
  
  // Analysis
  patterns: Pattern[];
  predictedOutcomes: PredictedOutcome[];
  
  // Risk
  riskAssessment: RiskAssessment;
  
  // Recommendation
  recommendation: DecisionRecommendation;
  
  // Uncertainty
  uncertaintyFactors: string[];
  confidenceInterval: { lower: number; upper: number };
  
  // Authority
  requiredAuthority: string;
  deadline?: number;
  
  // Audit
  preparedAt: number;
  preparedBy: string;
  version: number;
}

export interface DecisionResult {
  decisionId: string;
  action: 'approved' | 'rejected' | 'deferred' | 'escalated';
  authorityId: string;
  authorityName: string;
  timestamp: number;
  signature?: string;
  notes?: string;
}

class HumanDecisionPreparationEngine {
  private static instance: HumanDecisionPreparationEngine;
  private pendingDecisions: Map<string, PreparedDecision> = new Map();
  private decisionHistory: DecisionResult[] = [];
  private dataCollectors: Map<string, () => Promise<DataPoint[]>> = new Map();
  private patternAnalyzers: Map<string, (data: DataPoint[]) => Pattern[]> = new Map();

  private constructor() {
    this.initializeDefaultAnalyzers();
  }

  static getInstance(): HumanDecisionPreparationEngine {
    if (!HumanDecisionPreparationEngine.instance) {
      HumanDecisionPreparationEngine.instance = new HumanDecisionPreparationEngine();
    }
    return HumanDecisionPreparationEngine.instance;
  }

  private initializeDefaultAnalyzers(): void {
    // Register default pattern analyzers
    this.patternAnalyzers.set('frequency', (data) => {
      const valueCounts = new Map<string, number>();
      data.forEach(d => {
        const key = JSON.stringify(d.value);
        valueCounts.set(key, (valueCounts.get(key) || 0) + 1);
      });
      
      return Array.from(valueCounts.entries()).map(([value, count]) => ({
        id: `freq_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: `Frequency pattern: ${value.substring(0, 50)}`,
        frequency: count / data.length,
        confidence: Math.min(0.95, count / 10),
        relevance: count / data.length
      }));
    });

    this.patternAnalyzers.set('trend', (data) => {
      if (data.length < 2) return [];
      
      const numericData = data
        .filter(d => typeof d.value === 'number')
        .sort((a, b) => a.timestamp - b.timestamp);
      
      if (numericData.length < 2) return [];
      
      const first = numericData[0].value as number;
      const last = numericData[numericData.length - 1].value as number;
      const trend = last > first ? 'increasing' : last < first ? 'decreasing' : 'stable';
      
      return [{
        id: `trend_${Date.now()}`,
        name: `Trend: ${trend}`,
        frequency: 1,
        confidence: Math.min(0.9, numericData.length / 20),
        relevance: 0.8
      }];
    });
  }

  registerDataCollector(name: string, collector: () => Promise<DataPoint[]>): void {
    this.dataCollectors.set(name, collector);
  }

  registerPatternAnalyzer(name: string, analyzer: (data: DataPoint[]) => Pattern[]): void {
    this.patternAnalyzers.set(name, analyzer);
  }

  async prepareDecision(
    category: DecisionCategory,
    title: string,
    context: {
      requiredAuthority: string;
      deadline?: number;
      additionalData?: DataPoint[];
    }
  ): Promise<PreparedDecision> {
    const id = `decision_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // 1. Collect all data
    const dataPoints: DataPoint[] = [...(context.additionalData || [])];
    for (const [, collector] of this.dataCollectors) {
      try {
        const collected = await collector();
        dataPoints.push(...collected);
      } catch (error) {
        console.warn('Data collector failed:', error);
      }
    }
    
    // 2. Analyze patterns
    const patterns: Pattern[] = [];
    for (const [, analyzer] of this.patternAnalyzers) {
      try {
        const analyzed = analyzer(dataPoints);
        patterns.push(...analyzed);
      } catch (error) {
        console.warn('Pattern analyzer failed:', error);
      }
    }
    
    // 3. Predict outcomes
    const predictedOutcomes = this.predictOutcomes(dataPoints, patterns, category);
    
    // 4. Assess risk
    const riskAssessment = this.assessRisk(predictedOutcomes, category);
    
    // 5. Generate recommendation
    const recommendation = this.generateRecommendation(
      predictedOutcomes,
      riskAssessment,
      category
    );
    
    // 6. Calculate uncertainty
    const uncertaintyFactors = this.identifyUncertaintyFactors(dataPoints, patterns);
    const avgConfidence = patterns.length > 0
      ? patterns.reduce((sum, p) => sum + p.confidence, 0) / patterns.length
      : 0.5;
    
    const prepared: PreparedDecision = {
      id,
      category,
      title,
      summary: this.generateSummary(title, predictedOutcomes, recommendation),
      dataPoints,
      dataCompleteness: this.calculateDataCompleteness(dataPoints),
      patterns,
      predictedOutcomes,
      riskAssessment,
      recommendation,
      uncertaintyFactors,
      confidenceInterval: {
        lower: Math.max(0, avgConfidence - 0.15),
        upper: Math.min(1, avgConfidence + 0.15)
      },
      requiredAuthority: context.requiredAuthority,
      deadline: context.deadline,
      preparedAt: Date.now(),
      preparedBy: 'HumanDecisionPreparationEngine',
      version: 1
    };
    
    this.pendingDecisions.set(id, prepared);
    return prepared;
  }

  private predictOutcomes(
    data: DataPoint[],
    patterns: Pattern[],
    category: DecisionCategory
  ): PredictedOutcome[] {
    const outcomes: PredictedOutcome[] = [];
    
    // Base outcome from category
    const categoryOutcomes: Record<DecisionCategory, PredictedOutcome> = {
      financial: {
        id: 'fin_base',
        description: 'Financial impact based on historical patterns',
        probability: 0.7,
        impact: 'neutral',
        magnitude: 5,
        timeframe: '30 days'
      },
      legal: {
        id: 'legal_base',
        description: 'Legal compliance status',
        probability: 0.85,
        impact: 'neutral',
        magnitude: 7,
        timeframe: 'immediate'
      },
      medical: {
        id: 'med_base',
        description: 'Health outcome prediction',
        probability: 0.6,
        impact: 'neutral',
        magnitude: 8,
        timeframe: 'varies'
      },
      safety: {
        id: 'safety_base',
        description: 'Safety assessment outcome',
        probability: 0.9,
        impact: 'neutral',
        magnitude: 9,
        timeframe: 'immediate'
      },
      operational: {
        id: 'ops_base',
        description: 'Operational efficiency impact',
        probability: 0.75,
        impact: 'positive',
        magnitude: 4,
        timeframe: '7 days'
      },
      strategic: {
        id: 'strat_base',
        description: 'Strategic alignment outcome',
        probability: 0.65,
        impact: 'positive',
        magnitude: 6,
        timeframe: '90 days'
      }
    };
    
    outcomes.push(categoryOutcomes[category]);
    
    // Add pattern-based outcomes
    patterns.filter(p => p.confidence > 0.7).forEach(pattern => {
      outcomes.push({
        id: `outcome_${pattern.id}`,
        description: `Pattern-based: ${pattern.name}`,
        probability: pattern.confidence * 0.8,
        impact: pattern.relevance > 0.5 ? 'positive' : 'neutral',
        magnitude: Math.round(pattern.relevance * 10),
        timeframe: 'based on pattern'
      });
    });
    
    return outcomes;
  }

  private assessRisk(
    outcomes: PredictedOutcome[],
    category: DecisionCategory
  ): RiskAssessment {
    const negativeOutcomes = outcomes.filter(o => o.impact === 'negative');
    const avgMagnitude = outcomes.reduce((sum, o) => sum + o.magnitude, 0) / outcomes.length;
    
    let level: RiskLevel = 'low';
    if (negativeOutcomes.length > 2 || avgMagnitude > 7) level = 'critical';
    else if (negativeOutcomes.length > 1 || avgMagnitude > 5) level = 'high';
    else if (negativeOutcomes.length > 0 || avgMagnitude > 3) level = 'medium';
    
    // Category-specific risk adjustment
    if (['medical', 'safety', 'legal'].includes(category)) {
      if (level === 'low') level = 'medium';
      else if (level === 'medium') level = 'high';
    }
    
    return {
      level,
      factors: negativeOutcomes.map(o => o.description),
      mitigations: this.suggestMitigations(level, category),
      residualRisk: level === 'critical' ? 0.7 : level === 'high' ? 0.4 : level === 'medium' ? 0.2 : 0.05
    };
  }

  private suggestMitigations(level: RiskLevel, category: DecisionCategory): string[] {
    const baseMitigations = [
      'Document decision rationale',
      'Set up monitoring for outcomes',
      'Prepare contingency plan'
    ];
    
    if (level === 'high' || level === 'critical') {
      baseMitigations.push('Require secondary approval');
      baseMitigations.push('Implement staged rollout');
    }
    
    if (category === 'financial') {
      baseMitigations.push('Set budget limits');
    } else if (category === 'legal') {
      baseMitigations.push('Consult legal counsel');
    } else if (category === 'medical') {
      baseMitigations.push('Require medical professional review');
    }
    
    return baseMitigations;
  }

  private generateRecommendation(
    outcomes: PredictedOutcome[],
    risk: RiskAssessment,
    category: DecisionCategory
  ): DecisionRecommendation {
    const positiveOutcomes = outcomes.filter(o => o.impact === 'positive');
    const negativeOutcomes = outcomes.filter(o => o.impact === 'negative');
    
    const positiveScore = positiveOutcomes.reduce((sum, o) => sum + o.probability * o.magnitude, 0);
    const negativeScore = negativeOutcomes.reduce((sum, o) => sum + o.probability * o.magnitude, 0);
    
    let action: DecisionRecommendation['action'];
    let confidence: number;
    
    if (risk.level === 'critical') {
      action = 'escalate';
      confidence = 0.9;
    } else if (positiveScore > negativeScore * 2) {
      action = 'approve';
      confidence = Math.min(0.95, positiveScore / 10);
    } else if (negativeScore > positiveScore * 2) {
      action = 'reject';
      confidence = Math.min(0.95, negativeScore / 10);
    } else {
      action = 'defer';
      confidence = 0.5;
    }
    
    return {
      action,
      confidence,
      reasoning: [
        `Positive outcome score: ${positiveScore.toFixed(2)}`,
        `Negative outcome score: ${negativeScore.toFixed(2)}`,
        `Risk level: ${risk.level}`,
        `Category: ${category}`
      ],
      alternatives: action === 'reject' 
        ? ['Consider partial implementation', 'Request more data', 'Modify scope']
        : ['Proceed with monitoring', 'Implement in phases'],
      warnings: risk.factors
    };
  }

  private generateSummary(
    title: string,
    outcomes: PredictedOutcome[],
    recommendation: DecisionRecommendation
  ): string {
    const topOutcome = outcomes.sort((a, b) => b.probability - a.probability)[0];
    return `${title}: ${recommendation.action.toUpperCase()} recommended with ${(recommendation.confidence * 100).toFixed(0)}% confidence. Primary outcome: ${topOutcome?.description || 'Unknown'}`;
  }

  private calculateDataCompleteness(data: DataPoint[]): number {
    if (data.length === 0) return 0;
    const avgReliability = data.reduce((sum, d) => sum + d.reliability, 0) / data.length;
    const coverageFactor = Math.min(1, data.length / 10);
    return avgReliability * coverageFactor;
  }

  private identifyUncertaintyFactors(data: DataPoint[], patterns: Pattern[]): string[] {
    const factors: string[] = [];
    
    if (data.length < 5) factors.push('Limited data points available');
    if (patterns.length === 0) factors.push('No clear patterns identified');
    
    const lowReliabilityData = data.filter(d => d.reliability < 0.5);
    if (lowReliabilityData.length > data.length * 0.3) {
      factors.push('Significant portion of data has low reliability');
    }
    
    const lowConfidencePatterns = patterns.filter(p => p.confidence < 0.6);
    if (lowConfidencePatterns.length > patterns.length * 0.5) {
      factors.push('Pattern confidence is generally low');
    }
    
    return factors;
  }

  recordDecision(result: DecisionResult): void {
    this.decisionHistory.push(result);
    this.pendingDecisions.delete(result.decisionId);
  }

  getPendingDecisions(): PreparedDecision[] {
    return Array.from(this.pendingDecisions.values());
  }

  getDecisionHistory(): DecisionResult[] {
    return [...this.decisionHistory];
  }

  getDecision(id: string): PreparedDecision | undefined {
    return this.pendingDecisions.get(id);
  }
}

export const humanDecisionPreparationEngine = HumanDecisionPreparationEngine.getInstance();
