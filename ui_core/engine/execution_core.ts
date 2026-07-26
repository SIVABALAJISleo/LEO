/**
 * DETERMINISTIC EXECUTION CORE
 * Principles:
 * 1. No runtime reasoning.
 * 2. O(1) lookup via canonical key.
 * 3. Static asset delivery (CDN).
 */

import { ErrorCode } from "../gatekeeper/validator";

export class ExecutionCore {
  private static CDN_BASE = "/cdn/results";

  /**
   * MOCK MPHF (Minimal Perfect Hash Function)
   * In a real production build, this map is generated offline.
   */
  private static MPHF_MAP: Record<string, string> = {
    "finance|revenue|total|ytd|none": "1001",
    "finance|profit|gross|q3|region:us": "1002",
    "inventory|stock|available|now|warehouse:main": "2001",
    "ops|latency|p99|24h|service:api": "3001",
  };

  /**
   * Executes the query by looking up the ID and fetching from CDN.
   */
  public static async execute(canonicalKey: string): Promise<any> {
    const id = this.MPHF_MAP[canonicalKey];

    if (!id) {
      throw new Error(ErrorCode.NOT_SUPPORTED);
    }

    try {
      const response = await fetch(`${this.CDN_BASE}/${id}.json`);
      if (!response.ok) throw new Error("CDN_FETCH_FAILED");

      return await response.json();
    } catch (err) {
      console.error("Execution Error:", err);
      return {
        status: "ERROR",
        code: ErrorCode.NOT_SUPPORTED,
        suggestions: this.getSuggestions(canonicalKey),
      };
    }
  }

  private static getSuggestions(key: string): string[] {
    // Simple nearest-neighbor suggestion for the fallback system
    const keys = Object.keys(this.MPHF_MAP);
    return keys.filter((k) => k.split("|")[0] === key.split("|")[0]).slice(0, 3);
  }
}
