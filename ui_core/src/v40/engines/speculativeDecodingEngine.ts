export interface SpeculativeDecodingReport {
  draftAcceptedTokensCount: number;
  draftRejectedTokensCount: number;
  acceptanceRate: number;
  verificationLatencyReductionMs: number;
  totalSpeedupMultiplier: number;
}
export class SpeculativeDecodingEngine {
  public async verifyTokens(
    totalTokensNeeded: number,
    powerSaverMode: boolean,
  ): Promise<SpeculativeDecodingReport> {
    const res = await fetch("http://localhost:8000/api/v1/v40/engines/speculative", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ totalTokensNeeded, powerSaverMode }),
    });
    return res.json();
  }
}
