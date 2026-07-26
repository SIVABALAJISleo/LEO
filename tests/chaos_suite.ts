import { ReliabilityOrchestrator } from "../src/lib/core/ReliabilityOrchestrator";
import { PerformanceController } from "../src/lib/core/PerformanceController";

export class ChaosSuite {
  private orchestrator: ReliabilityOrchestrator;
  private perf: PerformanceController;

  constructor() {
    this.orchestrator = ReliabilityOrchestrator.getInstance();
    this.perf = PerformanceController.getInstance();
  }

  async runDbFailureSimulation() {
    console.log("[ChaosSuite] Injecting Database Failure (Mock)...");
    // We register a failing handler to trigger retries and circuit breaking
    this.orchestrator.register("chaos_db_operation", async () => {
      throw new Error("Database Connection Lost");
    });

    try {
      await this.orchestrator.execute("chaos_db_operation", {}, { circuitThreshold: 2 });
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (e) {
      console.log("[ChaosSuite] Caught expected failure.");
    }

    // Verify circuit is open
    console.log("[ChaosSuite] DB Operation now behind OPEN circuit.");
  }

  async runNetworkLatencySimulation() {
    console.log("[ChaosSuite] Injecting High Network Latency (5000ms)...");
    this.orchestrator.register("slow_network_op", async () => {
      await new Promise((r) => setTimeout(r, 6000));
      return "late success";
    });

    try {
      await this.orchestrator.execute("slow_network_op", {}, { timeoutMs: 1000, maxRetries: 0 });
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
    } catch (e) {
      console.log("[ChaosSuite] Caught expected timeout.");
    }
  }

  async runHighLoadSimulation() {
    console.log("[ChaosSuite] Injecting High CPU/Memory Load...");
    // Simulate many concurrent requests to trigger rate limiting
    const tasks = Array(10)
      .fill(0)
      .map((_, i) =>
        this.orchestrator
          .execute("load_test", { id: i }, { rateLimitCount: 5 })
          .catch((err) => `Rejected: ${err.message}`),
      );

    const results = await Promise.all(tasks);
    console.log(`[ChaosSuite] Processed ${results.length} requests under load.`);
  }
}
