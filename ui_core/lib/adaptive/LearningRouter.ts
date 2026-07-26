import { MoERouter } from "../intelligence/MoERouter";

interface RoutingRecord {
  query: string;
  expert: string;
  success: boolean;
  timestamp: number;
}

export class LearningRouter {
  private static instance: LearningRouter;
  private moe: MoERouter;
  private history: RoutingRecord[] = [];
  private successPatterns: Map<string, string> = new Map(); // query pattern -> expert

  private constructor() {
    this.moe = MoERouter.getInstance();
  }

  static getInstance(): LearningRouter {
    if (!LearningRouter.instance) {
      LearningRouter.instance = new LearningRouter();
    }
    return LearningRouter.instance;
  }

  async routeWithLearning(query: string): Promise<string> {
    // Check if we've seen similar queries before
    const pattern = this.extractPattern(query);
    const learnedExpert = this.successPatterns.get(pattern);

    let expert: string;
    if (learnedExpert) {
      expert = learnedExpert;
      console.log(`[LearningRouter] Using learned route: ${pattern} -> ${expert}`);
    } else {
      expert = await this.moe.route(query);
    }

    // Record the routing decision
    this.history.push({
      query,
      expert,
      success: true, // Would be updated based on actual execution result
      timestamp: Date.now(),
    });

    // Update learned patterns if this query type has been consistently routed
    this.updatePatterns();

    return expert;
  }

  recordSuccess(query: string, expert: string) {
    const pattern = this.extractPattern(query);
    this.successPatterns.set(pattern, expert);
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  recordFailure(query: string, expert: string) {
    // Remove failing patterns
    const pattern = this.extractPattern(query);
    this.successPatterns.delete(pattern);
  }

  private extractPattern(query: string): string {
    // Simple pattern extraction - first 2 words or key terms
    const words = query.toLowerCase().split(/\s+/).slice(0, 2);
    return words.join(" ");
  }

  private updatePatterns() {
    // Keep only recent history
    const cutoff = Date.now() - 24 * 60 * 60 * 1000; // 24 hours
    this.history = this.history.filter((r) => r.timestamp > cutoff);
  }

  getStats() {
    return {
      historySize: this.history.length,
      learnedPatterns: this.successPatterns.size,
    };
  }
}
