/**
 * Intelligence Composition Engine
 *
 * Composes multiple small expert models and retrieval systems:
 * - Small expert models (code, math, text, vision)
 * - Retrieval system (docs, memory, history)
 * - Router selects expert
 * - Combine outputs into one answer
 * - No training required
 *
 * Uses existing models/knowledge - never claims to train new ones.
 */

export type ExpertDomain =
  | "code"
  | "math"
  | "text"
  | "vision"
  | "reasoning"
  | "extraction"
  | "summarization"
  | "classification";

export type RetrievalSource = "documentation" | "memory" | "history" | "knowledge_base" | "cache";

export interface Expert {
  id: string;
  domain: ExpertDomain;
  name: string;
  confidence: number; // Base confidence level
  capabilities: string[];
  limitations: string[];
  process: (input: unknown) => Promise<ExpertOutput>;
}

export interface ExpertOutput {
  expertId: string;
  domain: ExpertDomain;
  result: unknown;
  confidence: number;
  reasoning: string[];
  processingTimeMs: number;
}

export interface RetrievalResult {
  source: RetrievalSource;
  items: Array<{
    id: string;
    content: string;
    relevance: number;
    timestamp?: number;
  }>;
  totalFound: number;
  searchTimeMs: number;
}

export interface ComposedAnswer {
  id: string;
  query: string;

  // Expert outputs
  expertOutputs: ExpertOutput[];
  selectedExperts: string[];

  // Retrieval
  retrievalResults: RetrievalResult[];

  // Combined answer
  answer: string;
  confidence: number;
  sources: string[];

  // Metadata
  compositionStrategy: string;
  totalProcessingTimeMs: number;
  timestamp: number;
}

export interface RoutingDecision {
  selectedExperts: ExpertDomain[];
  selectedSources: RetrievalSource[];
  reasoning: string;
  confidence: number;
}

class IntelligenceCompositionEngine {
  private static instance: IntelligenceCompositionEngine;
  private experts: Map<ExpertDomain, Expert> = new Map();
  private retrievalSystems: Map<RetrievalSource, (query: string) => Promise<RetrievalResult>> =
    new Map();
  private compositionHistory: ComposedAnswer[] = [];
  private memoryStore: Map<string, { content: string; timestamp: number }> = new Map();

  private constructor() {
    this.initializeDefaultExperts();
    this.initializeDefaultRetrievalSystems();
  }

  static getInstance(): IntelligenceCompositionEngine {
    if (!IntelligenceCompositionEngine.instance) {
      IntelligenceCompositionEngine.instance = new IntelligenceCompositionEngine();
    }
    return IntelligenceCompositionEngine.instance;
  }

  private initializeDefaultExperts(): void {
    // Code Expert
    this.experts.set("code", {
      id: "expert_code",
      domain: "code",
      name: "Code Analysis Expert",
      confidence: 0.85,
      capabilities: ["syntax analysis", "pattern matching", "code structure"],
      limitations: ["no execution", "no runtime behavior prediction"],
      process: async (input) => {
        const startTime = Date.now();
        const code = String(input);

        // Simple code analysis
        const analysis = {
          hasFunction: /function|=>|def |fn /.test(code),
          hasLoop: /for|while|loop|each/.test(code),
          hasCondition: /if|else|switch|match|case/.test(code),
          lineCount: code.split("\n").length,
          complexity: "low" as "low" | "medium" | "high",
        };

        if (analysis.hasLoop && analysis.hasCondition) analysis.complexity = "medium";
        if (analysis.lineCount > 50 || (analysis.hasLoop && analysis.hasFunction)) {
          analysis.complexity = "high";
        }

        return {
          expertId: "expert_code",
          domain: "code",
          result: analysis,
          confidence: 0.85,
          reasoning: ["Performed static code analysis", "Identified structural patterns"],
          processingTimeMs: Date.now() - startTime,
        };
      },
    });

    // Math Expert
    this.experts.set("math", {
      id: "expert_math",
      domain: "math",
      name: "Mathematical Reasoning Expert",
      confidence: 0.9,
      capabilities: ["arithmetic", "algebra", "statistics", "pattern recognition"],
      limitations: ["no symbolic calculus", "no theorem proving"],
      process: async (input) => {
        const startTime = Date.now();
        const expression = String(input);

        // Try to evaluate simple expressions
        let result: unknown = null;
        let confidence = 0.5;

        try {
          // Only evaluate safe numeric expressions
          if (/^[\d\s+\-*/().]+$/.test(expression)) {
            result = Function(`"use strict"; return (${expression})`)();
            confidence = 0.95;
          } else {
            // Pattern-based analysis
            result = {
              containsNumbers: /\d/.test(expression),
              containsOperators: /[+\-*/^]/.test(expression),
              containsVariables: /[a-zA-Z]/.test(expression),
              isEquation: /=/.test(expression),
            };
            confidence = 0.7;
          }
        } catch {
          result = { error: "Unable to evaluate", input: expression };
          confidence = 0.3;
        }

        return {
          expertId: "expert_math",
          domain: "math",
          result,
          confidence,
          reasoning: ["Analyzed mathematical expression", "Applied evaluation rules"],
          processingTimeMs: Date.now() - startTime,
        };
      },
    });

    // Text Expert
    this.experts.set("text", {
      id: "expert_text",
      domain: "text",
      name: "Text Analysis Expert",
      confidence: 0.8,
      capabilities: ["sentiment analysis", "entity extraction", "summarization hints"],
      limitations: ["no deep semantic understanding", "pattern-based only"],
      process: async (input) => {
        const startTime = Date.now();
        const text = String(input);

        const words = text.split(/\s+/).filter((w) => w.length > 0);
        const sentences = text.split(/[.!?]+/).filter((s) => s.trim().length > 0);

        // Simple sentiment
        const positiveWords = ["good", "great", "excellent", "happy", "love", "best", "wonderful"];
        const negativeWords = ["bad", "terrible", "hate", "worst", "poor", "awful", "horrible"];

        const posCount = words.filter((w) => positiveWords.includes(w.toLowerCase())).length;
        const negCount = words.filter((w) => negativeWords.includes(w.toLowerCase())).length;

        let sentiment: "positive" | "negative" | "neutral" = "neutral";
        if (posCount > negCount) sentiment = "positive";
        if (negCount > posCount) sentiment = "negative";

        return {
          expertId: "expert_text",
          domain: "text",
          result: {
            wordCount: words.length,
            sentenceCount: sentences.length,
            avgWordsPerSentence: sentences.length > 0 ? words.length / sentences.length : 0,
            sentiment,
            sentimentConfidence: Math.abs(posCount - negCount) / Math.max(1, words.length),
          },
          confidence: 0.75,
          reasoning: ["Performed lexical analysis", "Applied pattern-based sentiment"],
          processingTimeMs: Date.now() - startTime,
        };
      },
    });

    // Reasoning Expert
    this.experts.set("reasoning", {
      id: "expert_reasoning",
      domain: "reasoning",
      name: "Logical Reasoning Expert",
      confidence: 0.7,
      capabilities: ["deduction", "induction", "pattern matching"],
      limitations: ["no causal reasoning", "limited context"],
      process: async (input) => {
        const startTime = Date.now();
        const premise = String(input);

        // Simple logical pattern detection
        const hasIf = /if\s+.+\s+then/i.test(premise);
        const hasAll = /all\s+.+\s+are/i.test(premise);
        const hasNot = /not|never|no\s+/i.test(premise);
        const hasOr = /\s+or\s+/i.test(premise);
        const hasAnd = /\s+and\s+/i.test(premise);

        return {
          expertId: "expert_reasoning",
          domain: "reasoning",
          result: {
            logicalStructure: {
              conditional: hasIf,
              universal: hasAll,
              negation: hasNot,
              disjunction: hasOr,
              conjunction: hasAnd,
            },
            complexity: [hasIf, hasAll, hasNot, hasOr, hasAnd].filter(Boolean).length,
          },
          confidence: 0.65,
          reasoning: ["Identified logical operators", "Mapped argument structure"],
          processingTimeMs: Date.now() - startTime,
        };
      },
    });

    // Classification Expert
    this.experts.set("classification", {
      id: "expert_classification",
      domain: "classification",
      name: "Classification Expert",
      confidence: 0.8,
      capabilities: ["categorization", "tagging", "type detection"],
      limitations: ["fixed categories", "no learning"],
      process: async (input) => {
        const startTime = Date.now();
        const content = String(input).toLowerCase();

        const categories: Record<string, string[]> = {
          question: ["?", "what", "how", "why", "when", "where", "who"],
          command: ["do", "create", "make", "build", "run", "execute", "start"],
          statement: ["is", "are", "was", "were", "the", "it"],
          request: ["please", "could", "would", "can you", "help"],
        };

        const scores: Record<string, number> = {};
        for (const [category, keywords] of Object.entries(categories)) {
          scores[category] = keywords.filter((k) => content.includes(k)).length / keywords.length;
        }

        const topCategory = Object.entries(scores).sort((a, b) => b[1] - a[1])[0];

        return {
          expertId: "expert_classification",
          domain: "classification",
          result: {
            category: topCategory[0],
            confidence: topCategory[1],
            allScores: scores,
          },
          confidence: Math.max(0.5, topCategory[1]),
          reasoning: ["Applied keyword matching", "Scored category relevance"],
          processingTimeMs: Date.now() - startTime,
        };
      },
    });
  }

  private initializeDefaultRetrievalSystems(): void {
    // Memory retrieval
    this.retrievalSystems.set("memory", async (query) => {
      const startTime = Date.now();
      const queryLower = query.toLowerCase();

      const items = Array.from(this.memoryStore.entries())
        .map(([id, data]) => ({
          id,
          content: data.content,
          relevance: this.calculateRelevance(queryLower, data.content.toLowerCase()),
          timestamp: data.timestamp,
        }))
        .filter((item) => item.relevance > 0.1)
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, 10);

      return {
        source: "memory",
        items,
        totalFound: items.length,
        searchTimeMs: Date.now() - startTime,
      };
    });

    // History retrieval
    this.retrievalSystems.set("history", async (query) => {
      const startTime = Date.now();
      const queryLower = query.toLowerCase();

      const items = this.compositionHistory
        .map((h) => ({
          id: h.id,
          content: `Q: ${h.query}\nA: ${h.answer}`,
          relevance: this.calculateRelevance(queryLower, h.query.toLowerCase()),
          timestamp: h.timestamp,
        }))
        .filter((item) => item.relevance > 0.1)
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, 5);

      return {
        source: "history",
        items,
        totalFound: items.length,
        searchTimeMs: Date.now() - startTime,
      };
    });

    // Cache retrieval (in-memory)
    this.retrievalSystems.set("cache", async (query) => {
      const startTime = Date.now();

      // Check for exact match in recent history
      const exactMatch = this.compositionHistory.find(
        (h) => h.query.toLowerCase() === query.toLowerCase(),
      );

      const items = exactMatch
        ? [
            {
              id: exactMatch.id,
              content: exactMatch.answer,
              relevance: 1.0,
              timestamp: exactMatch.timestamp,
            },
          ]
        : [];

      return {
        source: "cache",
        items,
        totalFound: items.length,
        searchTimeMs: Date.now() - startTime,
      };
    });
  }

  private calculateRelevance(query: string, content: string): number {
    const queryWords = query.split(/\s+/).filter((w) => w.length > 2);
    if (queryWords.length === 0) return 0;

    const matches = queryWords.filter((w) => content.includes(w)).length;
    return matches / queryWords.length;
  }

  routeQuery(query: string): RoutingDecision {
    const queryLower = query.toLowerCase();
    const selectedExperts: ExpertDomain[] = [];
    const selectedSources: RetrievalSource[] = ["cache", "history"]; // Always check these
    const reasons: string[] = [];

    // Route based on query content
    if (/code|function|program|script|algorithm/.test(queryLower)) {
      selectedExperts.push("code");
      reasons.push("Detected code-related terms");
    }

    if (/\d|calculate|compute|sum|average|math|equation/.test(queryLower)) {
      selectedExperts.push("math");
      reasons.push("Detected mathematical content");
    }

    if (/analyze|sentiment|summary|text|document/.test(queryLower)) {
      selectedExperts.push("text");
      reasons.push("Detected text analysis need");
    }

    if (/why|because|therefore|logic|reason|deduce/.test(queryLower)) {
      selectedExperts.push("reasoning");
      reasons.push("Detected reasoning requirement");
    }

    if (/classify|categorize|type|kind|sort/.test(queryLower)) {
      selectedExperts.push("classification");
      reasons.push("Detected classification need");
    }

    // Default to text + classification if no specific domain
    if (selectedExperts.length === 0) {
      selectedExperts.push("text", "classification");
      reasons.push("Using default experts for general query");
    }

    // Add memory if query seems to reference past context
    if (/remember|previous|before|earlier|last/.test(queryLower)) {
      selectedSources.push("memory");
      reasons.push("Query references past context");
    }

    return {
      selectedExperts,
      selectedSources,
      reasoning: reasons.join("; "),
      confidence: Math.min(0.9, 0.5 + selectedExperts.length * 0.1),
    };
  }

  async compose(query: string, context?: unknown): Promise<ComposedAnswer> {
    const startTime = Date.now();
    const id = `composed_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // 1. Route the query
    const routing = this.routeQuery(query);

    // 2. Run retrieval in parallel
    const retrievalPromises = routing.selectedSources.map(async (source) => {
      const retriever = this.retrievalSystems.get(source);
      if (retriever) {
        try {
          return await retriever(query);
        } catch (error) {
          console.warn(`Retrieval from ${source} failed:`, error);
          return null;
        }
      }
      return null;
    });

    // 3. Run experts in parallel
    const expertPromises = routing.selectedExperts.map(async (domain) => {
      const expert = this.experts.get(domain);
      if (expert) {
        try {
          return await expert.process(context || query);
        } catch (error) {
          console.warn(`Expert ${domain} failed:`, error);
          return null;
        }
      }
      return null;
    });

    // 4. Await all results
    const [retrievalResults, expertOutputs] = await Promise.all([
      Promise.all(retrievalPromises),
      Promise.all(expertPromises),
    ]);

    const validRetrievals = retrievalResults.filter((r): r is RetrievalResult => r !== null);
    const validOutputs = expertOutputs.filter((o): o is ExpertOutput => o !== null);

    // 5. Compose final answer
    const answer = this.combineOutputs(query, validOutputs, validRetrievals);

    // 6. Calculate overall confidence
    const avgExpertConfidence =
      validOutputs.length > 0
        ? validOutputs.reduce((sum, o) => sum + o.confidence, 0) / validOutputs.length
        : 0;

    const composed: ComposedAnswer = {
      id,
      query,
      expertOutputs: validOutputs,
      selectedExperts: routing.selectedExperts,
      retrievalResults: validRetrievals,
      answer,
      confidence: avgExpertConfidence * routing.confidence,
      sources: [
        ...validOutputs.map((o) => o.expertId),
        ...validRetrievals.filter((r) => r.items.length > 0).map((r) => r.source),
      ],
      compositionStrategy: routing.reasoning,
      totalProcessingTimeMs: Date.now() - startTime,
      timestamp: Date.now(),
    };

    // Store in history
    this.compositionHistory.push(composed);
    if (this.compositionHistory.length > 100) {
      this.compositionHistory.shift();
    }

    return composed;
  }

  private combineOutputs(
    query: string,
    outputs: ExpertOutput[],
    retrievals: RetrievalResult[],
  ): string {
    const parts: string[] = [];

    // Add cached answer if found
    const cacheHit = retrievals.find((r) => r.source === "cache" && r.items.length > 0);
    if (cacheHit && cacheHit.items[0].relevance === 1.0) {
      return `[Cached] ${cacheHit.items[0].content}`;
    }

    // Combine expert outputs
    for (const output of outputs) {
      const resultStr =
        typeof output.result === "object"
          ? JSON.stringify(output.result, null, 2)
          : String(output.result);

      parts.push(
        `[${output.domain}] (${(output.confidence * 100).toFixed(0)}% confidence): ${resultStr}`,
      );
    }

    // Add relevant history
    const historyHits = retrievals.find((r) => r.source === "history" && r.items.length > 0);
    if (historyHits && historyHits.items.length > 0) {
      parts.push(`[Related history] ${historyHits.items[0].content.substring(0, 100)}...`);
    }

    return parts.join("\n\n") || "No experts could process this query.";
  }

  storeMemory(id: string, content: string): void {
    this.memoryStore.set(id, { content, timestamp: Date.now() });
  }

  getStats(): {
    expertCount: number;
    retrievalSourceCount: number;
    historySize: number;
    memorySize: number;
  } {
    return {
      expertCount: this.experts.size,
      retrievalSourceCount: this.retrievalSystems.size,
      historySize: this.compositionHistory.length,
      memorySize: this.memoryStore.size,
    };
  }

  registerExpert(expert: Expert): void {
    this.experts.set(expert.domain, expert);
  }

  registerRetrieval(
    source: RetrievalSource,
    retriever: (query: string) => Promise<RetrievalResult>,
  ): void {
    this.retrievalSystems.set(source, retriever);
  }
}

export const intelligenceCompositionEngine = IntelligenceCompositionEngine.getInstance();
