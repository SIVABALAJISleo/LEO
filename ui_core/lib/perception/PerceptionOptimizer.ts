export type QualityLevel = "draft" | "preview" | "final";

export interface RefinementStep {
  level: QualityLevel;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  compute: () => Promise<any>;
  qualityScore: number;
}

export class PerceptionOptimizer {
  private static instance: PerceptionOptimizer;
  private readonly PERCEPTUAL_THRESHOLD = 0.85;

  private constructor() {}

  static getInstance(): PerceptionOptimizer {
    if (!PerceptionOptimizer.instance) {
      PerceptionOptimizer.instance = new PerceptionOptimizer();
    }
    return PerceptionOptimizer.instance;
  }

  async progressiveCompute<T>(steps: RefinementStep[]): Promise<T> {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let result: any = null;

    for (const step of steps) {
      console.log(`[PerceptionOptimizer] Computing at ${step.level} quality`);
      result = await step.compute();

      // Early exit if quality is good enough
      if (step.qualityScore >= this.PERCEPTUAL_THRESHOLD) {
        console.log(
          `[PerceptionOptimizer] Quality sufficient (${step.qualityScore}), stopping early`,
        );
        break;
      }
    }

    return result;
  }

  estimateQualityScore(level: QualityLevel): number {
    const scores: Record<QualityLevel, number> = {
      draft: 0.6,
      preview: 0.85,
      final: 1.0,
    };
    return scores[level];
  }
}
