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
    const lower = url.toLowerCase();
    let credibilityWeight = 0.5; // base trust
    let isTrustedPartner = false;
    let sourceDomain = "unknown-domain";

    try {
      const parts = url.replace("https://", "").replace("http://", "").split("/");
      sourceDomain = parts[0] || "unknown-domain";
    } catch (e) {
      sourceDomain = "malformed-url";
    }

    if (lower.includes(".gov") || lower.includes(".edu") || lower.includes("arxiv.org")) {
      credibilityWeight = 0.95;
      isTrustedPartner = true;
    } else if (lower.includes("github.com") || lower.includes("intel.com")) {
      credibilityWeight = 0.88;
      isTrustedPartner = true;
    } else if (lower.includes("blog") || lower.includes("wiki")) {
      credibilityWeight = 0.65;
    }

    return {
      url,
      sourceDomain,
      credibilityWeight,
      isTrustedPartner,
    };
  }
}
