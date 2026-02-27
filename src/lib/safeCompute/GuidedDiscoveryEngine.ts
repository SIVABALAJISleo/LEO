/**
 * Guided Discovery Engine
 * 
 * Guides humans through discovery of unknowns:
 * - Hypothesis generator
 * - Simulation & risk bounding
 * - Experiment planner
 * - Cost / safety estimator
 * - Human executes experiment in reality
 * 
 * NEVER executes experiments - only prepares and guides.
 */

export type DiscoveryDomain =
  | 'scientific'
  | 'engineering'
  | 'business'
  | 'medical'
  | 'safety'
  | 'optimization';

export type HypothesisStatus =
  | 'proposed'
  | 'under_review'
  | 'ready_for_test'
  | 'testing'
  | 'validated'
  | 'refuted'
  | 'inconclusive';

export interface Variable {
  name: string;
  type: 'independent' | 'dependent' | 'controlled';
  currentValue?: unknown;
  expectedRange?: { min: number; max: number };
  unit?: string;
}

export interface Hypothesis {
  id: string;
  domain: DiscoveryDomain;
  statement: string;
  variables: Variable[];
  assumptions: string[];
  predictions: string[];
  status: HypothesisStatus;
  confidence: number;
  createdAt: number;
  updatedAt: number;
}

export interface RiskBound {
  category: string;
  worstCase: string;
  probability: number;
  impact: 'low' | 'medium' | 'high' | 'critical';
  mitigation: string;
}

export interface SimulationResult {
  hypothesisId: string;
  scenarioName: string;
  predictedOutcome: unknown;
  confidenceInterval: { lower: number; upper: number };
  assumptions: string[];
  limitations: string[];
  riskBounds: RiskBound[];
  simulatedAt: number;
}

export interface ExperimentStep {
  order: number;
  action: string;
  duration: string;
  resources: string[];
  safetyChecks: string[];
  successCriteria: string;
  failureCriteria: string;
  contingency: string;
}

export interface ExperimentPlan {
  id: string;
  hypothesisId: string;
  title: string;
  objective: string;
  
  // Planning
  steps: ExperimentStep[];
  requiredResources: string[];
  estimatedDuration: string;
  
  // Cost estimation
  estimatedCost: {
    minimum: number;
    expected: number;
    maximum: number;
    currency: string;
    breakdown: Record<string, number>;
  };
  
  // Safety
  safetyRating: 'safe' | 'moderate' | 'high_risk' | 'extreme';
  safetyPrecautions: string[];
  emergencyProcedures: string[];
  requiredCertifications: string[];
  
  // Authority
  requiredApprovals: string[];
  ethicsReviewRequired: boolean;
  regulatoryRequirements: string[];
  
  // Metadata
  createdAt: number;
  createdBy: string;
  version: number;
}

export interface ExperimentResult {
  planId: string;
  hypothesisId: string;
  executedBy: string;
  executedAt: number;
  
  outcome: 'success' | 'failure' | 'partial' | 'inconclusive';
  observations: string[];
  measurements: Record<string, unknown>;
  unexpectedEvents: string[];
  
  conclusionSupportsHypothesis: boolean | null;
  confidenceLevel: number;
  nextSteps: string[];
}

class GuidedDiscoveryEngine {
  private static instance: GuidedDiscoveryEngine;
  private hypotheses: Map<string, Hypothesis> = new Map();
  private simulations: Map<string, SimulationResult[]> = new Map();
  private plans: Map<string, ExperimentPlan> = new Map();
  private results: Map<string, ExperimentResult[]> = new Map();

  private constructor() {}

  static getInstance(): GuidedDiscoveryEngine {
    if (!GuidedDiscoveryEngine.instance) {
      GuidedDiscoveryEngine.instance = new GuidedDiscoveryEngine();
    }
    return GuidedDiscoveryEngine.instance;
  }

  generateHypothesis(
    domain: DiscoveryDomain,
    observation: string,
    context?: {
      existingKnowledge?: string[];
      constraints?: string[];
      goals?: string[];
    }
  ): Hypothesis {
    const id = `hyp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Extract potential variables from observation
    const variables = this.extractVariables(observation, domain);
    
    // Generate assumptions based on domain
    const assumptions = this.generateAssumptions(domain, context);
    
    // Generate predictions
    const predictions = this.generatePredictions(observation, variables, domain);
    
    // Formulate hypothesis statement
    const statement = this.formulateStatement(observation, variables, predictions);
    
    const hypothesis: Hypothesis = {
      id,
      domain,
      statement,
      variables,
      assumptions,
      predictions,
      status: 'proposed',
      confidence: this.calculateInitialConfidence(variables, assumptions),
      createdAt: Date.now(),
      updatedAt: Date.now()
    };
    
    this.hypotheses.set(id, hypothesis);
    return hypothesis;
  }

  private extractVariables(observation: string, domain: DiscoveryDomain): Variable[] {
    const variables: Variable[] = [];
    
    // Domain-specific variable extraction patterns
    const patterns: Record<DiscoveryDomain, RegExp[]> = {
      scientific: [/(\w+)\s+(increases?|decreases?)/gi, /when\s+(\w+)\s+changes/gi],
      engineering: [/(\w+)\s+(performance|efficiency|capacity)/gi, /(\w+)\s+load/gi],
      business: [/(revenue|cost|profit|growth|conversion)\s+(\w+)/gi],
      medical: [/(dosage|treatment|symptom|condition)\s+(\w+)/gi],
      safety: [/(risk|hazard|exposure|protection)\s+(\w+)/gi],
      optimization: [/(time|space|cost|quality)\s+(\w+)/gi]
    };
    
    const domainPatterns = patterns[domain] || [];
    
    for (const pattern of domainPatterns) {
      const matches = observation.matchAll(pattern);
      for (const match of matches) {
        const varName = match[1] || match[2];
        if (varName && !variables.find(v => v.name.toLowerCase() === varName.toLowerCase())) {
          variables.push({
            name: varName,
            type: variables.length === 0 ? 'independent' : 'dependent'
          });
        }
      }
    }
    
    // Ensure at least one variable
    if (variables.length === 0) {
      variables.push({
        name: 'primary_factor',
        type: 'independent'
      });
      variables.push({
        name: 'observed_effect',
        type: 'dependent'
      });
    }
    
    return variables;
  }

  private generateAssumptions(
    domain: DiscoveryDomain,
    context?: { existingKnowledge?: string[]; constraints?: string[] }
  ): string[] {
    const baseAssumptions: Record<DiscoveryDomain, string[]> = {
      scientific: [
        'Conditions remain controlled during observation',
        'Measurement instruments are calibrated',
        'No external interference'
      ],
      engineering: [
        'System operates within design parameters',
        'Components meet specifications',
        'Environmental conditions are nominal'
      ],
      business: [
        'Market conditions remain stable',
        'No major competitive disruptions',
        'Customer behavior follows historical patterns'
      ],
      medical: [
        'Patient population is representative',
        'No undisclosed conditions',
        'Treatment adherence is maintained'
      ],
      safety: [
        'Safety protocols are followed',
        'Equipment is properly maintained',
        'Personnel are trained'
      ],
      optimization: [
        'Constraints are correctly specified',
        'Objective function is valid',
        'Data is representative'
      ]
    };
    
    const assumptions = [...(baseAssumptions[domain] || [])];
    
    if (context?.existingKnowledge) {
      assumptions.push(`Based on: ${context.existingKnowledge.slice(0, 2).join(', ')}`);
    }
    
    if (context?.constraints) {
      assumptions.push(`Constrained by: ${context.constraints.slice(0, 2).join(', ')}`);
    }
    
    return assumptions;
  }

  private generatePredictions(
    observation: string,
    variables: Variable[],
    domain: DiscoveryDomain
  ): string[] {
    const predictions: string[] = [];
    
    const independent = variables.find(v => v.type === 'independent');
    const dependent = variables.find(v => v.type === 'dependent');
    
    if (independent && dependent) {
      predictions.push(
        `If ${independent.name} increases, ${dependent.name} will change predictably`
      );
      predictions.push(
        `The relationship between ${independent.name} and ${dependent.name} is measurable`
      );
    }
    
    // Domain-specific predictions
    if (domain === 'business') {
      predictions.push('The effect will be observable within the measurement period');
    } else if (domain === 'scientific') {
      predictions.push('The effect is reproducible under similar conditions');
    } else if (domain === 'engineering') {
      predictions.push('The system behavior is deterministic');
    }
    
    return predictions;
  }

  private formulateStatement(
    observation: string,
    variables: Variable[],
    predictions: string[]
  ): string {
    const independent = variables.find(v => v.type === 'independent');
    const dependent = variables.find(v => v.type === 'dependent');
    
    if (independent && dependent) {
      return `Changes in ${independent.name} cause observable changes in ${dependent.name}, as suggested by: "${observation.substring(0, 100)}"`;
    }
    
    return `The observed phenomenon ("${observation.substring(0, 100)}") follows a predictable pattern that can be tested.`;
  }

  private calculateInitialConfidence(
    variables: Variable[],
    assumptions: string[]
  ): number {
    // Base confidence
    let confidence = 0.5;
    
    // More defined variables = higher confidence
    confidence += Math.min(0.2, variables.length * 0.05);
    
    // More assumptions (potentially limiting) = slightly lower confidence
    confidence -= Math.min(0.1, assumptions.length * 0.02);
    
    // Variables with ranges have higher confidence
    const rangedVars = variables.filter(v => v.expectedRange);
    confidence += rangedVars.length * 0.05;
    
    return Math.max(0.1, Math.min(0.9, confidence));
  }

  simulateScenario(
    hypothesisId: string,
    scenario: {
      name: string;
      conditions: Record<string, unknown>;
    }
  ): SimulationResult {
    const hypothesis = this.hypotheses.get(hypothesisId);
    if (!hypothesis) {
      throw new Error(`Hypothesis ${hypothesisId} not found`);
    }
    
    // Simulate based on hypothesis predictions
    const predictedOutcome = this.predictOutcome(hypothesis, scenario.conditions);
    
    // Generate risk bounds
    const riskBounds = this.assessRiskBounds(hypothesis, scenario);
    
    const result: SimulationResult = {
      hypothesisId,
      scenarioName: scenario.name,
      predictedOutcome,
      confidenceInterval: {
        lower: hypothesis.confidence * 0.7,
        upper: Math.min(1, hypothesis.confidence * 1.3)
      },
      assumptions: hypothesis.assumptions,
      limitations: [
        'Simulation is model-based, not empirical',
        'Unknown factors may affect real outcome',
        'Confidence bounds are estimates'
      ],
      riskBounds,
      simulatedAt: Date.now()
    };
    
    // Store simulation
    const existing = this.simulations.get(hypothesisId) || [];
    existing.push(result);
    this.simulations.set(hypothesisId, existing);
    
    return result;
  }

  private predictOutcome(
    hypothesis: Hypothesis,
    conditions: Record<string, unknown>
  ): unknown {
    // Simple prediction based on hypothesis structure
    const independent = hypothesis.variables.find(v => v.type === 'independent');
    const dependent = hypothesis.variables.find(v => v.type === 'dependent');
    
    if (independent && dependent) {
      const independentValue = conditions[independent.name];
      if (typeof independentValue === 'number' && independent.expectedRange) {
        const normalized = (independentValue - independent.expectedRange.min) /
          (independent.expectedRange.max - independent.expectedRange.min);
        
        return {
          [dependent.name]: {
            predicted: normalized * 100,
            unit: dependent.unit || 'units',
            confidence: hypothesis.confidence
          }
        };
      }
    }
    
    return {
      outcome: 'Prediction requires more specific variable definitions',
      confidence: hypothesis.confidence * 0.5
    };
  }

  private assessRiskBounds(
    hypothesis: Hypothesis,
    scenario: { name: string; conditions: Record<string, unknown> }
  ): RiskBound[] {
    const risks: RiskBound[] = [];
    
    // Domain-specific risks
    const domainRisks: Record<DiscoveryDomain, RiskBound> = {
      scientific: {
        category: 'Experimental validity',
        worstCase: 'Results not reproducible',
        probability: 0.2,
        impact: 'medium',
        mitigation: 'Multiple trials with controls'
      },
      engineering: {
        category: 'System failure',
        worstCase: 'Component damage',
        probability: 0.15,
        impact: 'high',
        mitigation: 'Use test environment, incremental testing'
      },
      business: {
        category: 'Market response',
        worstCase: 'Customer loss',
        probability: 0.25,
        impact: 'medium',
        mitigation: 'A/B testing, limited rollout'
      },
      medical: {
        category: 'Patient safety',
        worstCase: 'Adverse reaction',
        probability: 0.1,
        impact: 'critical',
        mitigation: 'Ethics review, informed consent, monitoring'
      },
      safety: {
        category: 'Personnel safety',
        worstCase: 'Injury',
        probability: 0.05,
        impact: 'critical',
        mitigation: 'PPE, safety protocols, supervision'
      },
      optimization: {
        category: 'Performance degradation',
        worstCase: 'System slowdown',
        probability: 0.3,
        impact: 'low',
        mitigation: 'Rollback capability, monitoring'
      }
    };
    
    risks.push(domainRisks[hypothesis.domain]);
    
    // Add general risks
    risks.push({
      category: 'Unknown unknowns',
      worstCase: 'Unforeseen factors affect results',
      probability: 0.1,
      impact: 'medium',
      mitigation: 'Document all observations, be prepared to adapt'
    });
    
    return risks;
  }

  createExperimentPlan(
    hypothesisId: string,
    options?: {
      budgetLimit?: number;
      timeLimit?: string;
      safetyPriority?: 'low' | 'medium' | 'high';
    }
  ): ExperimentPlan {
    const hypothesis = this.hypotheses.get(hypothesisId);
    if (!hypothesis) {
      throw new Error(`Hypothesis ${hypothesisId} not found`);
    }
    
    const id = `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Generate steps based on hypothesis
    const steps = this.generateExperimentSteps(hypothesis, options);
    
    // Estimate costs
    const estimatedCost = this.estimateCost(hypothesis, steps, options?.budgetLimit);
    
    // Assess safety
    const safetyAssessment = this.assessExperimentSafety(hypothesis, steps);
    
    // Determine required approvals
    const approvals = this.determineRequiredApprovals(hypothesis, safetyAssessment);
    
    const plan: ExperimentPlan = {
      id,
      hypothesisId,
      title: `Experiment: ${hypothesis.statement.substring(0, 50)}...`,
      objective: `Test whether: ${hypothesis.predictions[0] || hypothesis.statement}`,
      steps,
      requiredResources: this.identifyResources(hypothesis, steps),
      estimatedDuration: options?.timeLimit || this.estimateDuration(steps),
      estimatedCost,
      safetyRating: safetyAssessment.rating,
      safetyPrecautions: safetyAssessment.precautions,
      emergencyProcedures: safetyAssessment.emergencyProcedures,
      requiredCertifications: safetyAssessment.certifications,
      requiredApprovals: approvals.approvals,
      ethicsReviewRequired: approvals.ethicsRequired,
      regulatoryRequirements: approvals.regulations,
      createdAt: Date.now(),
      createdBy: 'GuidedDiscoveryEngine',
      version: 1
    };
    
    this.plans.set(id, plan);
    
    // Update hypothesis status
    hypothesis.status = 'ready_for_test';
    hypothesis.updatedAt = Date.now();
    
    return plan;
  }

  private generateExperimentSteps(
    hypothesis: Hypothesis,
    options?: { safetyPriority?: 'low' | 'medium' | 'high' }
  ): ExperimentStep[] {
    const steps: ExperimentStep[] = [];
    const safetyLevel = options?.safetyPriority || 'medium';
    
    // Step 1: Setup
    steps.push({
      order: 1,
      action: 'Prepare experimental environment and verify all conditions',
      duration: '1-2 hours',
      resources: ['Equipment', 'Documentation', 'Safety gear'],
      safetyChecks: ['Environment verified', 'Equipment calibrated'],
      successCriteria: 'All preparation checklist items complete',
      failureCriteria: 'Any preparation item incomplete',
      contingency: 'Delay experiment until preparation is complete'
    });
    
    // Step 2: Baseline measurement
    steps.push({
      order: 2,
      action: `Measure baseline values for: ${hypothesis.variables.map(v => v.name).join(', ')}`,
      duration: '30 minutes',
      resources: ['Measurement tools', 'Recording system'],
      safetyChecks: ['Instruments calibrated', 'Recording system active'],
      successCriteria: 'All baseline values recorded with acceptable variance',
      failureCriteria: 'Measurement variance exceeds acceptable limits',
      contingency: 'Re-calibrate instruments and re-measure'
    });
    
    // Step 3: Variable manipulation
    const independent = hypothesis.variables.find(v => v.type === 'independent');
    steps.push({
      order: 3,
      action: `Apply controlled change to ${independent?.name || 'independent variable'}`,
      duration: 'Variable (depends on experiment)',
      resources: ['Control mechanisms', 'Monitoring equipment'],
      safetyChecks: safetyLevel === 'high' 
        ? ['All safety limits verified', 'Emergency stop tested', 'Observer present']
        : ['Safety limits verified'],
      successCriteria: 'Variable changed as planned within tolerance',
      failureCriteria: 'Unable to achieve target change or safety limit reached',
      contingency: 'Stop immediately, record state, assess for retry'
    });
    
    // Step 4: Observation
    steps.push({
      order: 4,
      action: 'Record all observations and measurements during response period',
      duration: 'As specified in protocol',
      resources: ['Recording equipment', 'Timer', 'Observation logs'],
      safetyChecks: ['Continuous monitoring active'],
      successCriteria: 'All planned data points collected',
      failureCriteria: 'Data collection incomplete or corrupted',
      contingency: 'Note gaps in data, assess if retrial needed'
    });
    
    // Step 5: Analysis
    steps.push({
      order: 5,
      action: 'Analyze collected data against hypothesis predictions',
      duration: '1-4 hours',
      resources: ['Analysis tools', 'Reference data', 'Hypothesis documentation'],
      safetyChecks: ['Data backup complete'],
      successCriteria: 'Analysis complete with statistical significance determined',
      failureCriteria: 'Insufficient data for meaningful analysis',
      contingency: 'Additional data collection may be required'
    });
    
    // Step 6: Documentation
    steps.push({
      order: 6,
      action: 'Document all results, observations, and conclusions',
      duration: '1-2 hours',
      resources: ['Documentation template', 'Raw data', 'Analysis results'],
      safetyChecks: ['All data preserved'],
      successCriteria: 'Complete documentation suitable for review',
      failureCriteria: 'Documentation incomplete or inconsistent',
      contingency: 'Complete documentation before proceeding'
    });
    
    return steps;
  }

  private estimateCost(
    hypothesis: Hypothesis,
    steps: ExperimentStep[],
    budgetLimit?: number
  ): ExperimentPlan['estimatedCost'] {
    // Base costs by domain
    const baseCosts: Record<DiscoveryDomain, number> = {
      scientific: 500,
      engineering: 1000,
      business: 200,
      medical: 2000,
      safety: 800,
      optimization: 100
    };
    
    const base = baseCosts[hypothesis.domain];
    const stepCost = steps.length * 50;
    const variableCost = hypothesis.variables.length * 100;
    
    const expected = base + stepCost + variableCost;
    
    return {
      minimum: Math.round(expected * 0.7),
      expected: Math.round(expected),
      maximum: budgetLimit ? Math.min(budgetLimit, expected * 1.5) : Math.round(expected * 1.5),
      currency: 'USD',
      breakdown: {
        'Equipment/Setup': Math.round(base * 0.4),
        'Labor': Math.round(base * 0.3),
        'Materials': Math.round(stepCost),
        'Analysis': Math.round(variableCost * 0.5),
        'Contingency': Math.round(expected * 0.15)
      }
    };
  }

  private assessExperimentSafety(
    hypothesis: Hypothesis,
    steps: ExperimentStep[]
  ): {
    rating: ExperimentPlan['safetyRating'];
    precautions: string[];
    emergencyProcedures: string[];
    certifications: string[];
  } {
    const domainSafety: Record<DiscoveryDomain, ExperimentPlan['safetyRating']> = {
      scientific: 'moderate',
      engineering: 'moderate',
      business: 'safe',
      medical: 'high_risk',
      safety: 'high_risk',
      optimization: 'safe'
    };
    
    const basePrecautions = [
      'Review all steps before beginning',
      'Ensure emergency contacts are available',
      'Document any deviations from plan'
    ];
    
    const domainPrecautions: Record<DiscoveryDomain, string[]> = {
      scientific: ['Use appropriate PPE', 'Follow lab protocols'],
      engineering: ['Verify system isolation', 'Use lockout/tagout procedures'],
      business: ['Inform stakeholders', 'Have rollback plan ready'],
      medical: ['Obtain informed consent', 'Have medical personnel on standby'],
      safety: ['Full safety gear required', 'Buddy system mandatory'],
      optimization: ['Create system backup', 'Monitor performance metrics']
    };
    
    return {
      rating: domainSafety[hypothesis.domain],
      precautions: [...basePrecautions, ...(domainPrecautions[hypothesis.domain] || [])],
      emergencyProcedures: [
        'Stop all activities immediately',
        'Secure the area',
        'Contact emergency services if needed',
        'Document the incident',
        'Notify project lead'
      ],
      certifications: hypothesis.domain === 'medical' 
        ? ['IRB approval', 'Clinical research certification']
        : hypothesis.domain === 'safety'
        ? ['Safety officer certification', 'First aid training']
        : []
    };
  }

  private determineRequiredApprovals(
    hypothesis: Hypothesis,
    safety: { rating: ExperimentPlan['safetyRating'] }
  ): {
    approvals: string[];
    ethicsRequired: boolean;
    regulations: string[];
  } {
    const approvals: string[] = ['Project lead'];
    const regulations: string[] = [];
    let ethicsRequired = false;
    
    if (safety.rating === 'high_risk' || safety.rating === 'extreme') {
      approvals.push('Safety officer');
      approvals.push('Department head');
    }
    
    if (hypothesis.domain === 'medical') {
      ethicsRequired = true;
      approvals.push('IRB (Institutional Review Board)');
      regulations.push('HIPAA compliance');
      regulations.push('Good Clinical Practice (GCP)');
    }
    
    if (hypothesis.domain === 'safety') {
      regulations.push('OSHA requirements');
    }
    
    return { approvals, ethicsRequired, regulations };
  }

  private identifyResources(
    hypothesis: Hypothesis,
    steps: ExperimentStep[]
  ): string[] {
    const resources = new Set<string>();
    
    steps.forEach(step => {
      step.resources.forEach(r => resources.add(r));
    });
    
    // Add domain-specific resources
    if (hypothesis.domain === 'scientific') {
      resources.add('Laboratory access');
    } else if (hypothesis.domain === 'engineering') {
      resources.add('Test environment');
    }
    
    return Array.from(resources);
  }

  private estimateDuration(steps: ExperimentStep[]): string {
    // Simple estimation based on step count
    const hours = steps.length * 2;
    if (hours <= 8) return `${hours} hours`;
    if (hours <= 40) return `${Math.ceil(hours / 8)} days`;
    return `${Math.ceil(hours / 40)} weeks`;
  }

  recordResult(result: ExperimentResult): void {
    const existing = this.results.get(result.hypothesisId) || [];
    existing.push(result);
    this.results.set(result.hypothesisId, existing);
    
    // Update hypothesis status
    const hypothesis = this.hypotheses.get(result.hypothesisId);
    if (hypothesis) {
      if (result.conclusionSupportsHypothesis === true) {
        hypothesis.status = 'validated';
      } else if (result.conclusionSupportsHypothesis === false) {
        hypothesis.status = 'refuted';
      } else {
        hypothesis.status = 'inconclusive';
      }
      hypothesis.confidence = result.confidenceLevel;
      hypothesis.updatedAt = Date.now();
    }
  }

  getHypothesis(id: string): Hypothesis | undefined {
    return this.hypotheses.get(id);
  }

  getPlan(id: string): ExperimentPlan | undefined {
    return this.plans.get(id);
  }

  getSimulations(hypothesisId: string): SimulationResult[] {
    return this.simulations.get(hypothesisId) || [];
  }

  getResults(hypothesisId: string): ExperimentResult[] {
    return this.results.get(hypothesisId) || [];
  }

  getAllHypotheses(): Hypothesis[] {
    return Array.from(this.hypotheses.values());
  }
}

export const guidedDiscoveryEngine = GuidedDiscoveryEngine.getInstance();
