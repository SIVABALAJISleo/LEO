// LEO AI V31 — Phase 13 Prefix Reuse Engine
// Purpose: Reuse identical prompt prefixes in enterprise workflows and repeated contexts.
// Goal: Avoid duplicate computation.

export interface PrefixCacheEntry {
  prefixHash: string;
  prefixLengthTokens: number;
  lastUsedTimestamp: number;
  hitCount: number;
}

export interface PrefixEvaluation {
  query: string;
  prefixFound: boolean;
  prefixLengthTokens: number;
  tokensBypassed: number;
  latencySavedMs: number;
  kvCacheSavedMb: number;
}

export class PrefixReuseEngine {
  private cache: Record<string, PrefixCacheEntry> = {
    // Simulate enterprise standard system prefixes
    "system-prompt-v31-audit": {
      prefixHash: "system-prompt-v31-audit",
      prefixLengthTokens: 1024,
      lastUsedTimestamp: Date.now(),
      hitCount: 15,
    },
    "regional-context-emea": {
      prefixHash: "regional-context-emea",
      prefixLengthTokens: 512,
      lastUsedTimestamp: Date.now(),
      hitCount: 8,
    },
  };

  evaluateQueryPrefix(query: string): PrefixEvaluation {
    const qLower = query.toLowerCase();
    let prefixFound = false;
    let prefixLengthTokens = 0;
    let targetPrefix = "";

    if (qLower.includes("audit") || qLower.includes("comply") || qLower.includes("certify")) {
      prefixFound = true;
      targetPrefix = "system-prompt-v31-audit";
      prefixLengthTokens = this.cache[targetPrefix].prefixLengthTokens;
      this.cache[targetPrefix].hitCount++;
      this.cache[targetPrefix].lastUsedTimestamp = Date.now();
    } else if (qLower.includes("emea") || qLower.includes("region") || qLower.includes("europe")) {
      prefixFound = true;
      targetPrefix = "regional-context-emea";
      prefixLengthTokens = this.cache[targetPrefix].prefixLengthTokens;
      this.cache[targetPrefix].hitCount++;
      this.cache[targetPrefix].lastUsedTimestamp = Date.now();
    }

    // Heuristic: If prompt is very long, assume a generic 256 token shared workspace prefix is matched
    if (!prefixFound && query.length > 150) {
      prefixFound = true;
      prefixLengthTokens = 256;
    }

    const tokensBypassed = prefixFound ? prefixLengthTokens : 0;
    // Latency saved is ~0.4ms per bypassed token (prefill avoidance)
    const latencySavedMs = prefixFound ? Math.round(tokensBypassed * 0.38) : 0;
    // KV Cache saved: each token is ~0.003MB in FP16
    const kvCacheSavedMb = parseFloat((tokensBypassed * 0.003).toFixed(3));

    return {
      query,
      prefixFound,
      prefixLengthTokens,
      tokensBypassed,
      latencySavedMs,
      kvCacheSavedMb,
    };
  }

  getCacheEntries(): PrefixCacheEntry[] {
    return Object.values(this.cache);
  }
}
