/**
 * Summary Memory
 * Rolling conversation summaries to avoid full history recomputation.
 */

export interface ConversationTurn {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

export interface Summary {
  content: string;
  turnCount: number;
  createdAt: number;
}

export class SummaryMemory {
  private static instance: SummaryMemory;
  private history: ConversationTurn[] = [];
  private summaries: Summary[] = [];

  private readonly MAX_TURNS_BEFORE_SUMMARY = 10;
  private readonly MAX_RECENT_TURNS = 5;

  private constructor() {}

  static getInstance(): SummaryMemory {
    if (!SummaryMemory.instance) {
      SummaryMemory.instance = new SummaryMemory();
    }
    return SummaryMemory.instance;
  }

  /**
   * Add conversation turn
   */
  addTurn(role: "user" | "assistant", content: string): void {
    this.history.push({
      role,
      content,
      timestamp: Date.now(),
    });

    // Auto-summarize if history gets long
    if (this.history.length >= this.MAX_TURNS_BEFORE_SUMMARY) {
      this.summarize();
    }
  }

  /**
   * Get context for next inference (summary + recent turns)
   */
  getContext(): string {
    const parts: string[] = [];

    // Include all summaries
    if (this.summaries.length > 0) {
      parts.push("Previous conversation summary:");
      parts.push(this.summaries.map((s) => s.content).join("\n\n"));
      parts.push("---");
    }

    // Include recent turns
    const recentTurns = this.history.slice(-this.MAX_RECENT_TURNS);
    if (recentTurns.length > 0) {
      parts.push("Recent messages:");
      parts.push(recentTurns.map((t) => `${t.role}: ${t.content}`).join("\n"));
    }

    return parts.join("\n");
  }

  /**
   * Create summary of old conversation
   */
  private summarize(): void {
    // Summarize everything except recent turns
    const toSummarize = this.history.slice(0, -this.MAX_RECENT_TURNS);

    if (toSummarize.length === 0) return;

    // Mock summarization - real implementation would use LLM
    const topics = this.extractTopics(toSummarize);
    const summary = `Discussed: ${topics.join(", ")}`;

    this.summaries.push({
      content: summary,
      turnCount: toSummarize.length,
      createdAt: Date.now(),
    });

    // Keep only recent turns
    this.history = this.history.slice(-this.MAX_RECENT_TURNS);

    console.log(`[SummaryMemory] Summarized ${toSummarize.length} turns`);
  }

  private extractTopics(turns: ConversationTurn[]): string[] {
    // Simple keyword extraction
    const words = turns
      .map((t) => t.content.toLowerCase())
      .join(" ")
      .split(/\s+/);
    const wordCounts = new Map<string, number>();

    for (const word of words) {
      if (word.length > 4) {
        wordCounts.set(word, (wordCounts.get(word) || 0) + 1);
      }
    }

    return Array.from(wordCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([word]) => word);
  }

  /**
   * Clear all history
   */
  clear(): void {
    this.history = [];
    this.summaries = [];
  }

  getStats() {
    return {
      currentTurns: this.history.length,
      summaryCount: this.summaries.length,
      totalTurnsSummarized: this.summaries.reduce((sum, s) => sum + s.turnCount, 0),
    };
  }
}
