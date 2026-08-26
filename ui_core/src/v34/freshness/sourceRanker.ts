// LEO AI V34 — Source Ranker
// Capabilities: Assign credibility ratings to documents, rank reference URLs, and manage trust weights.

export interface SourceRank {
  url: string;
  sourceDomain: string;
  credibilityWeight: number; // 0.0 to 1.0
  isTrustedPartner: boolean;
}

export class SourceRanker {
  rankUrl(url: string): SourceRank {
    let credibilityWeight = 0.5; // base trust
    let isTrustedPartner = false;
    let sourceDomain = "unknown-domain";

    try {
      const parsed = new URL(url.startsWith("http") ? url : `https://${url}`);
      const hostname = parsed.hostname.toLowerCase();
      sourceDomain = hostname;

      if (
        hostname.endsWith(".gov") ||
        hostname.endsWith(".edu") ||
        hostname === "arxiv.org" ||
        hostname.endsWith(".arxiv.org")
      ) {
        credibilityWeight = 0.95;
        isTrustedPartner = true;
      } else if (
        hostname === "github.com" ||
        hostname.endsWith(".github.com") ||
        hostname === "intel.com" ||
        hostname.endsWith(".intel.com")
      ) {
        credibilityWeight = 0.88;
        isTrustedPartner = true;
      } else if (hostname.includes("blog") || hostname.includes("wiki")) {
        credibilityWeight = 0.65;
      }
    } catch {
      sourceDomain = "malformed-url";
    }

    return {
      url,
      sourceDomain,
      credibilityWeight,
      isTrustedPartner,
    };
  }
}
