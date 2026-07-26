// LEO AI V36 — Contradiction Resolver
// Resolves structural overlaps and conflicting assertions across sources.

export class ContradictionResolver {
  public resolveConflict(
    primary: string,
    secondary: string,
    primaryConf: number,
    secondaryConf: number,
  ): { resolvedText: string; resolvedConfidence: number; flagged: boolean } {
    if (primaryConf >= secondaryConf) {
      return {
        resolvedText: primary,
        resolvedConfidence: primaryConf,
        flagged: Math.abs(primaryConf - secondaryConf) < 0.05,
      };
    }
    return {
      resolvedText: secondary,
      resolvedConfidence: secondaryConf,
      flagged: Math.abs(primaryConf - secondaryConf) < 0.05,
    };
  }
}
