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
