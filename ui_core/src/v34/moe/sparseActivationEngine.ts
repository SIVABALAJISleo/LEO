// LEO AI V34 — Sparse Activation Engine
// Capabilities: Manage expert activation arrays, offload inactive weights, and audit active byte sizes.

export interface ExpertActivationStatus {
  expertId: string;
  name: string;
  isActive: boolean;
  allocationBytes: number;
}

export class SparseActivationEngine {
  private activeStates = new Map<string, ExpertActivationStatus>([
    [
      "exp-code",
      {
        expertId: "exp-code",
        name: "Code Expert",
        isActive: false,
        allocationBytes: 256 * 1024 * 1024,
      },
    ],
    [
      "exp-math",
      {
        expertId: "exp-math",
        name: "Math Expert",
        isActive: false,
        allocationBytes: 256 * 1024 * 1024,
      },
    ],
    [
      "exp-logic",
      {
        expertId: "exp-logic",
        name: "Logic Expert",
        isActive: false,
        allocationBytes: 256 * 1024 * 1024,
      },
    ],
    [
      "exp-default",
      {
        expertId: "exp-default",
        name: "General Expert",
        isActive: true,
        allocationBytes: 128 * 1024 * 1024,
      },
    ],
  ]);

  activateExpert(expertId: string): ExpertActivationStatus[] {
    this.activeStates.forEach((state, id) => {
      if (id === expertId) {
        state.isActive = true;
      } else if (id !== "exp-default") {
        state.isActive = false; // offload inactive ones
      }
      this.activeStates.set(id, state);
    });

    return Array.from(this.activeStates.values());
  }

  getStates(): ExpertActivationStatus[] {
    return Array.from(this.activeStates.values());
  }
}
