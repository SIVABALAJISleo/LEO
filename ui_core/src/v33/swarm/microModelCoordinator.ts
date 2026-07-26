// LEO AI V33 — Micro Model Coordinator
// Capabilities: Delegate queries to specific micro-model experts.

export interface SpecialistModel {
  id: string;
  role: "coding" | "planning" | "memory" | "retrieval" | "workflow";
  name: string;
  modelSizeBytes: number;
  accuracyScore: number;
}

export interface SwarmAssignment {
  query: string;
  assignedSpecialistId: string;
  secondarySpecialistId?: string;
  coordinationOverheadMs: number;
}

export class MicroModelCoordinator {
  private specialists: SpecialistModel[] = [
    {
      id: "sp-code-3b",
      role: "coding",
      name: "LEO Coding Expert v33 (3B)",
      modelSizeBytes: 3 * 1024 * 1024 * 1024,
      accuracyScore: 0.93,
    },
    {
      id: "sp-plan-1b",
      role: "planning",
      name: "LEO Planner v33 (1.1B)",
      modelSizeBytes: 1.1 * 1024 * 1024 * 1024,
      accuracyScore: 0.89,
    },
    {
      id: "sp-mem-0.5b",
      role: "memory",
      name: "LEO Association memory (0.5B)",
      modelSizeBytes: 500 * 1024 * 1024,
      accuracyScore: 0.91,
    },
    {
      id: "sp-retr-0.5b",
      role: "retrieval",
      name: "LEO GraphRAG retrieval (0.5B)",
      modelSizeBytes: 500 * 1024 * 1024,
      accuracyScore: 0.92,
    },
    {
      id: "sp-work-2b",
      role: "workflow",
      name: "LEO Workflow automator (2.2B)",
      modelSizeBytes: 2.2 * 1024 * 1024 * 1024,
      accuracyScore: 0.9,
    },
  ];

  assignTask(query: string): SwarmAssignment {
    const lower = query.toLowerCase();
    let selected: SpecialistModel = this.specialists[4]; // Default to workflow
    let secondary: SpecialistModel | undefined;

    if (
      lower.includes("code") ||
      lower.includes("function") ||
      lower.includes("class") ||
      lower.includes("bug")
    ) {
      selected = this.specialists[0]; // Coding
      secondary = this.specialists[1]; // Planning secondary
    } else if (lower.includes("plan") || lower.includes("step") || lower.includes("milestone")) {
      selected = this.specialists[1]; // Planning
      secondary = this.specialists[4]; // Workflow secondary
    } else if (lower.includes("remember") || lower.includes("memor") || lower.includes("history")) {
      selected = this.specialists[2]; // Memory
    } else if (
      lower.includes("search") ||
      lower.includes("retrieve") ||
      lower.includes("rag") ||
      lower.includes("find")
    ) {
      selected = this.specialists[3]; // Retrieval
      secondary = this.specialists[2]; // Memory secondary
    }

    return {
      query,
      assignedSpecialistId: selected.id,
      secondarySpecialistId: secondary?.id,
      coordinationOverheadMs: parseFloat((Math.random() * 2 + 1).toFixed(2)), // 1-3ms routing overhead
    };
  }

  getSpecialists(): SpecialistModel[] {
    return this.specialists;
  }
}
