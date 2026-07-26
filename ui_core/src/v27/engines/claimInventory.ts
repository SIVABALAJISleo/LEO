// V27 — Phase 1 Claim Inventory
// Holds the inventory of claims extracted from V18-V26 architectures

export type ClaimStatus = "UNVERIFIED" | "PROVEN" | "UNPROVEN";

export interface AuditClaim {
  claimId: string;
  claim: string;
  target: string;
  targetValue: number;
  operator: ">=" | "<=";
  status: ClaimStatus;
  measuredValue: number | null;
  confidence: number | null;
}

export class ClaimInventory {
  private claims: AuditClaim[] = [];

  constructor() {
    this.initializeInventory();
  }

  private initializeInventory() {
    this.claims = [
      {
        claimId: "C-REAS",
        claim: "Reasoning Accuracy",
        target: "Reasoning >= 95%",
        targetValue: 0.95,
        operator: ">=",
        status: "UNVERIFIED",
        measuredValue: null,
        confidence: null,
      },
      {
        claimId: "C-HALL",
        claim: "Hallucination Rate",
        target: "Hallucination <= 1%",
        targetValue: 0.01,
        operator: "<=",
        status: "UNVERIFIED",
        measuredValue: null,
        confidence: null,
      },
      {
        claimId: "C-MEMO",
        claim: "Memory Consistency",
        target: "Memory >= 98%",
        targetValue: 0.98,
        operator: ">=",
        status: "UNVERIFIED",
        measuredValue: null,
        confidence: null,
      },
      {
        claimId: "C-SEAR",
        claim: "Search Quality",
        target: "Search >= 99%",
        targetValue: 0.99,
        operator: ">=",
        status: "UNVERIFIED",
        measuredValue: null,
        confidence: null,
      },
      {
        claimId: "C-RAGG",
        claim: "RAG Quality",
        target: "RAG >= 99%",
        targetValue: 0.99,
        operator: ">=",
        status: "UNVERIFIED",
        measuredValue: null,
        confidence: null,
      },
      {
        claimId: "C-AGEN",
        claim: "Agent Quality",
        target: "Agent >= 98%",
        targetValue: 0.98,
        operator: ">=",
        status: "UNVERIFIED",
        measuredValue: null,
        confidence: null,
      },
      {
        claimId: "C-ENTR",
        claim: "Enterprise Reliability",
        target: "Enterprise Reliability >= 99%",
        targetValue: 0.99,
        operator: ">=",
        status: "UNVERIFIED",
        measuredValue: null,
        confidence: null,
      },
    ];
  }

  getClaims(): AuditClaim[] {
    return this.claims;
  }

  updateClaim(claimId: string, measuredValue: number, confidence: number, status: ClaimStatus) {
    const claim = this.claims.find((c) => c.claimId === claimId);
    if (claim) {
      claim.measuredValue = parseFloat(measuredValue.toFixed(4));
      claim.confidence = parseFloat(confidence.toFixed(4));
      claim.status = status;
    }
  }
}
