import os
import re

TS_FILES = {
    "activeLearningEngine.ts": """
export interface TrainingPriorityItem {
  queryText: string;
  uncertaintyScore: number;
  entropyMetric: number;
  priorityVerdict: "HighPriority_Queue" | "Normal_Queue" | "Skip_LowValue";
}
export class ActiveLearningEngine {
  private trainingQueue: TrainingPriorityItem[] = [];
  public async evaluatePriority(statement: string): Promise<TrainingPriorityItem> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/active_learning", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ statement })
    });
    const item = await res.json();
    if (item.priorityVerdict !== "Skip_LowValue") {
      this.trainingQueue.push(item);
    }
    return item;
  }
  public getQueue(): TrainingPriorityItem[] { return this.trainingQueue; }
}
""",
    "advancedMemorySystem.ts": """
export interface MemoryBlock {
  id: string; category: "semantic" | "episodic" | "project" | "user" | "scientific";
  content: string; importance: number; timestamp: number;
}
export interface CacheLookupResult {
  hit: boolean; value: string; sourceType: "prompt" | "embedding" | "response" | "reasoning"; similarityScore: number;
}
export class AdvancedMemorySystem {
  public async queryCache(prompt: string): Promise<CacheLookupResult> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/memory/query", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });
    return res.json();
  }
  public async addMemory(category: string, content: string, importance: number): Promise<void> {
    await fetch("http://localhost:8000/api/v1/v40/engines/memory/add", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, content, importance })
    });
  }
  public async getMemories(): Promise<MemoryBlock[]> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/memory/all");
    return res.json();
  }
}
""",
    "autonomousResearchSystem.ts": """
export interface LiteraturePaper { id: string; title: string; coreInsight: string; }
export interface ResearchGapReport {
  analyzedPapers: LiteraturePaper[]; detectedGaps: string[]; proposedHypotheses: string[]; experimentPlan: string;
}
export class AutonomousResearchSystem {
  public async analyzeLiterature(queryField: string): Promise<ResearchGapReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/research", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ queryField })
    });
    return res.json();
  }
}
""",
    "curriculumLearningEngine.ts": """
export interface CurriculumStep { stepId: string; label: string; difficulty: "Easy" | "Medium" | "Hard"; dependencyIds: string[]; acquired: boolean; }
export interface CurriculumReport { stages: CurriculumStep[]; overallProgress: number; activeTargetStep?: string; }
export class CurriculumLearningEngine {
  public async evaluateCurriculumProgress(): Promise<CurriculumReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/curriculum");
    return res.json();
  }
  public async completeStep(stepId: string): Promise<void> {
    await fetch("http://localhost:8000/api/v1/v40/engines/curriculum/complete", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ stepId })
    });
  }
}
""",
    "graphIntelligenceEngine.ts": """
export interface NetworkNode { id: string; name: string; category: string; }
export interface NetworkEdge { sourceId: string; targetId: string; predicate: string; relevance: number; }
export interface GraphTraceReport { traversedNodes: string[]; causalChain: string; hopsResolved: number; dependencyDiscovered: boolean; }
export class GraphIntelligenceEngine {
  public async traceCausality(startName: string, endName: string): Promise<GraphTraceReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/graph/trace", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ startName, endName })
    });
    return res.json();
  }
}
""",
    "intelligencePerComputeOptimizer.ts": """
export interface OptimizationMetrics { reasoningPerFlopPercent: number; knowledgePerGbMb: number; accuracyPerWattMultiplier: number; utilityPerDollarScore: number; scientificAccuracyRate: number; overallScore: number; }
export class IntelligencePerComputeOptimizer {
  public async aggregateOptimizerMetrics(ramLimitGb: number, powerMode: string, quantizationBits: number): Promise<OptimizationMetrics> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/optimizer", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ramLimitGb, powerMode, quantizationBits })
    });
    return res.json();
  }
}
""",
    "mambaHybridEngine.ts": """
export interface MambaTelemetry { contextLengthTokens: number; memoryUsageMb: number; attentionFlops: number; mambaFlops: number; speedupVsTransformer: number; }
export class MambaHybridEngine {
  public async projectScalingMetrics(contextLength: number): Promise<MambaTelemetry> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/mamba", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contextLength })
    });
    return res.json();
  }
}
""",
    "mixtureOfExpertsEngine.ts": """
export interface ExpertGateReport { selectedExperts: string[]; activeWeights: number[]; gateConfidence: number; unactivatedExpertsCount: number; reason: string; }
export class MixtureOfExpertsEngine {
  public async routeToExperts(prompt: string): Promise<ExpertGateReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/moe", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt })
    });
    return res.json();
  }
}
""",
    "modelCompressionEngine.ts": """
export interface CompressionDirectives { quantizationBitrate: number; loraRank: number; pruningRatio: number; expectedMemoryMb: number; precisionMode: "FP16" | "INT8" | "INT4" | "Ternary_1.58b"; }
export class ModelCompressionEngine {
  public async evaluateCompression(ramLimitGb: number): Promise<CompressionDirectives> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/compression", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ramLimitGb })
    });
    return res.json();
  }
}
""",
    "multiAgentSystem.ts": """
export interface AgentAction { agentName: string; contribution: string; confidenceScore: number; }
export interface AgentDebateReport { transcript: AgentAction[]; consensusScore: number; finalVerdict: string; }
export class MultiAgentSystem {
  public async executeAgentWorkflow(question: string): Promise<AgentDebateReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/agents", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    return res.json();
  }
}
""",
    "scientificReasoningEngine.ts": """
export interface ScientificHypothesis { claim: string; causalFactors: string[]; evidenceWeight: number; contradictions: string[]; }
export interface ScienceEvaluation { hypotheses: ScientificHypothesis[]; proposedExperiment: string; reproducibilityConfidence: number; }
export class ScientificReasoningEngine {
  public async evaluateResearchClaim(claimText: string): Promise<ScienceEvaluation> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/scientific", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claimText })
    });
    return res.json();
  }
}
""",
    "selfImprovementEngine.ts": """
export interface ExceptionLog { id: string; sourceModule: string; exceptionMessage: string; critiqueText: string; timestamp: number; }
export interface OptimizationPatch { patchId: string; actionScript: string; scoreBefore: number; scoreAfter: number; deployed: boolean; }
export interface SelfImprovementReport { loggedExceptions: ExceptionLog[]; activePatches: OptimizationPatch[]; improvementGainRatio: number; }
export class SelfImprovementEngine {
  public async logException(module: string, message: string): Promise<SelfImprovementReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/improvement/log", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ module, message })
    });
    return res.json();
  }
}
""",
    "sparseComputationEngine.ts": """
export interface SparsityDirectives { activeHeadsCount: number; sparsityRatio: number; conditionalComputeGate: boolean; flopsSaved: number; }
export class SparseComputationEngine {
  public async prescribeSparsity(attentionHeadsCount: number, ramLimitGb: number): Promise<SparsityDirectives> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/sparse", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ attentionHeadsCount, ramLimitGb })
    });
    return res.json();
  }
}
""",
    "speculativeDecodingEngine.ts": """
export interface SpeculativeDecodingReport { draftAcceptedTokensCount: number; draftRejectedTokensCount: number; acceptanceRate: number; verificationLatencyReductionMs: number; totalSpeedupMultiplier: number; }
export class SpeculativeDecodingEngine {
  public async verifyTokens(totalTokensNeeded: number, powerSaverMode: boolean): Promise<SpeculativeDecodingReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/speculative", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ totalTokensNeeded, powerSaverMode })
    });
    return res.json();
  }
}
""",
    "worldModelEngine.ts": """
export interface SimulationStep { index: number; modelCategory: string; simulatedAction: string; expectedState: string; riskFactor: number; }
export interface SimulationReport { overallSafetyScore: number; simulationTrace: SimulationStep[]; replanAdvised: boolean; }
export class WorldModelEngine {
  public async runSimulation(actions: string[]): Promise<SimulationReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/world", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ actions })
    });
    return res.json();
  }
}
"""
}

def migrate_frontend():
    base_dir = "C:/Users/sivab/OneDrive/Documents/HYPER/LEO-main/ui_core/src/v40/engines"
    for filename, content in TS_FILES.items():
        filepath = os.path.join(base_dir, filename)
        with open(filepath, "w") as f:
            f.write(content.strip() + "\n")
            
    print("Frontend SDKs migrated to async API wrappers.")

if __name__ == "__main__":
    migrate_frontend()
