// LEO AI V30 — Phase 12 Model Cascade Engine
// Escalates query evaluation progressively from Tiny (1B) parameters up to Large (70B) parameters.

export type CascadeModelSize = "Tiny_1B" | "Small_7B" | "Medium_13B" | "Large_70B";

export interface CascadeStep {
  modelType: CascadeModelSize;
  estimatedComplexity: number;
  reasoningPassed: boolean;
  computeCostSec: number;
}

export class AdaptiveModelCascade {
  evaluateQuery(query: string): CascadeStep[] {
    const steps: CascadeStep[] = [];
    const isVeryComplex =
      query.length > 50 ||
      query.toLowerCase().includes("proof") ||
      query.toLowerCase().includes("scientific");
    const isPhysicsHeavy =
      query.toLowerCase().includes("constraint") || query.toLowerCase().includes("motion");

    // Step 1: Always route to Tiny Model (1B)
    steps.push({
      modelType: "Tiny_1B",
      estimatedComplexity: 0.25,
      reasoningPassed: !isVeryComplex && !isPhysicsHeavy,
      computeCostSec: 0.04,
    });

    // Step 2: Route to Small Model (7B) if complexity check fails
    if (isVeryComplex || isPhysicsHeavy) {
      steps.push({
        modelType: "Small_7B",
        estimatedComplexity: 0.55,
        reasoningPassed: !isVeryComplex, // fails if very complex
        computeCostSec: 0.12,
      });
    }

    // Step 3: Route to Medium Model (13B) if logical verification fails
    if (isVeryComplex) {
      steps.push({
        modelType: "Medium_13B",
        estimatedComplexity: 0.78,
        reasoningPassed: query.length < 90, // fails if ultra long query
        computeCostSec: 0.28,
      });
    }

    // Step 4: Route to Large Model (70B) as final fallback
    if (isVeryComplex && query.length >= 90) {
      steps.push({
        modelType: "Large_70B",
        estimatedComplexity: 0.96,
        reasoningPassed: true,
        computeCostSec: 1.15,
      });
    }

    return steps;
  }
}
