// LEO AI V31 — Phase 8 Training Efficiency System
// Capabilities: QLoRA, LoRA, Gradient Checkpointing, Gradient Accumulation. Minimizes parameter retraining cost.

export type FinetuningStrategy = "FullParameter" | "LoRA" | "QLoRA_INT4";

export interface RetrainingCostReport {
  strategy: FinetuningStrategy;
  trainableParamsMillions: number;
  vramRequiredGb: number;
  gradientAccumulationSteps: number;
  checkpointingActive: boolean;
  relativeCostFactor: number; // e.g. 0.05 representing 20x savings (1/20)
  trainingSpeedTokensSec: number;
}

export class TrainingEfficiencyEngine {
  calculateFinetuningMetrics(
    strategy: FinetuningStrategy, 
    baseParamsBillions: number = 7.0,
    gradientAccumulationSteps: number = 4,
    checkpointingActive: boolean = true
  ): RetrainingCostReport {
    const baseTrainableParams = baseParamsBillions * 1000; // in Millions
    
    let trainableParamsMillions = 0;
    let vramRequiredGb = 0;
    let relativeCostFactor = 1.0;
    let trainingSpeedTokensSec = 0;

    if (strategy === "FullParameter") {
      trainableParamsMillions = baseTrainableParams;
      vramRequiredGb = baseParamsBillions * 16; // 16GB per billion params for FP16 training
      relativeCostFactor = 1.0;
      trainingSpeedTokensSec = 850;
      
      if (checkpointingActive) {
        vramRequiredGb *= 0.6; // saves activation memory
      }
    } else if (strategy === "LoRA") {
      trainableParamsMillions = baseTrainableParams * 0.008; // 0.8% params trainable
      vramRequiredGb = baseParamsBillions * 4.5;
      relativeCostFactor = 0.08;
      trainingSpeedTokensSec = 2200;
      
      if (checkpointingActive) {
        vramRequiredGb *= 0.7;
      }
    } else {
      // QLoRA INT4
      trainableParamsMillions = baseTrainableParams * 0.008;
      vramRequiredGb = baseParamsBillions * 1.8; // INT4 quantized base weights
      relativeCostFactor = 0.04; // ~25x cost reduction
      trainingSpeedTokensSec = 1400; // slightly slower than LoRA due to dequantization overhead
      
      if (checkpointingActive) {
        vramRequiredGb *= 0.75;
      }
    }

    // Apply gradient accumulation scaling
    if (gradientAccumulationSteps > 1) {
      trainingSpeedTokensSec = Math.round(trainingSpeedTokensSec * (1 - (0.05 * Math.log2(gradientAccumulationSteps))));
    }

    return {
      strategy,
      trainableParamsMillions: parseFloat(trainableParamsMillions.toFixed(1)),
      vramRequiredGb: parseFloat(vramRequiredGb.toFixed(2)),
      gradientAccumulationSteps,
      checkpointingActive,
      relativeCostFactor: parseFloat(relativeCostFactor.toFixed(3)),
      trainingSpeedTokensSec
    };
  }
}
