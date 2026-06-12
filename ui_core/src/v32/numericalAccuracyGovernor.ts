// LEO AI V32 — Phase 11 Numerical Accuracy Governor
// Capabilities: precision analysis, approximation tracking, error bounds.
// Purpose: Reduce scientific computation floating point errors.

export interface OperationErrorBounds {
  operationName: string;
  nominalValue: number;
  minPossibleValue: number;
  maxPossibleValue: number;
  worstCaseErrorMargin: number;
  precisionLossSeverity: "Negligible" | "Warning" | "Critical";
}

export class NumericalAccuracyGovernor {
  analyzePrecision(operationName: string, inputs: number[], operator: "+" | "-" | "*" | "/"): OperationErrorBounds {
    // Simulate floating point precision analysis: worse error margins for divisions or multiplications of very small/large floats
    let nominal = 0;
    let worstCaseError = 0.0000001;

    if (operator === "+") {
      nominal = inputs.reduce((acc, v) => acc + v, 0);
      worstCaseError = inputs.length * Number.EPSILON;
    } else if (operator === "-") {
      nominal = inputs[0] - inputs.slice(1).reduce((acc, v) => acc + v, 0);
      worstCaseError = inputs.length * Number.EPSILON;
    } else if (operator === "*") {
      nominal = inputs.reduce((acc, v) => acc * v, 1);
      worstCaseError = nominal * inputs.length * 2 * Number.EPSILON;
    } else {
      nominal = inputs[0] / (inputs[1] || 1);
      // Division by a very small number can lead to severe error amplification
      if (Math.abs(inputs[1]) < 0.0001) {
        worstCaseError = 0.05;
      } else {
        worstCaseError = (nominal / (inputs[1] || 1)) * Number.EPSILON;
      }
    }

    const minPossibleValue = nominal - worstCaseError;
    const maxPossibleValue = nominal + worstCaseError;
    
    let severity: "Negligible" | "Warning" | "Critical" = "Negligible";
    if (worstCaseError > 0.01) {
      severity = "Critical";
    } else if (worstCaseError > 0.00001) {
      severity = "Warning";
    }

    return {
      operationName,
      nominalValue: parseFloat(nominal.toFixed(8)),
      minPossibleValue: parseFloat(minPossibleValue.toFixed(8)),
      maxPossibleValue: parseFloat(maxPossibleValue.toFixed(8)),
      worstCaseErrorMargin: parseFloat(worstCaseError.toFixed(8)),
      precisionLossSeverity: severity
    };
  }
}
