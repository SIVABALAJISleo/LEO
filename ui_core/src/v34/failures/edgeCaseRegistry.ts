// LEO AI V34 — Edge Case Registry
// Capabilities: Index known error conditions, register trigger parameters, and manage lookup hashes.

export interface EdgeCaseRecord {
  caseId: string;
  triggerCondition: string;
  reproductionHash: string;
  impactLevel: "critical" | "warning" | "low";
}

export class EdgeCaseRegistry {
  private registry = new Map<string, EdgeCaseRecord>([
    [
      "oom-65k",
      {
        caseId: "ec-oom-65k",
        triggerCondition: "Context length > 65536 on FP16 CPU execution",
        reproductionHash: "h-ec-01-v34",
        impactLevel: "critical",
      },
    ],
    [
      "precision-degrad",
      {
        caseId: "ec-precision",
        triggerCondition: "Clamping weights to 1-bit on logical reasoning tasks",
        reproductionHash: "h-ec-02-v34",
        impactLevel: "warning",
      },
    ],
  ]);

  registerCase(
    trigger: string,
    hash: string,
    impact: "critical" | "warning" | "low",
  ): EdgeCaseRecord {
    const caseId = `ec-v34-${Math.random().toString(36).substring(7)}`;
    const record: EdgeCaseRecord = {
      caseId,
      triggerCondition: trigger,
      reproductionHash: hash,
      impactLevel: impact,
    };
    this.registry.set(hash, record);
    return record;
  }

  getRecords(): EdgeCaseRecord[] {
    return Array.from(this.registry.values());
  }
}
