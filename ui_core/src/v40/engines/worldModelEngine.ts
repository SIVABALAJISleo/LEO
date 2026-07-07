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
