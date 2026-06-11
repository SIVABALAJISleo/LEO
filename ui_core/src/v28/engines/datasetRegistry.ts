// V28 — Phase 2 Dataset Registry
// Tracks Dataset Name, Version, Creation Date, Sample Count, and Source hashes

export interface RegisteredDataset {
  name: string;
  version: string;
  creationDate: string;
  sampleCount: number;
  source: string;
  contentHash: string;
}

export class DatasetRegistry {
  private datasets: RegisteredDataset[] = [];

  constructor() {
    this.seedRegistry();
  }

  private seedRegistry() {
    this.datasets = [
      {
        name: "Antigravity-Real-Reasoning-Workloads",
        version: "1.2.0",
        creationDate: "2026-06-10",
        sampleCount: 100000,
        source: "production-logs & user-conversations",
        contentHash: "sha256-d7a9f8f8b88d3e2322329381c1c1c1f1f2e2"
      },
      {
        name: "Antigravity-Adversarial-RedTeam-Prompts",
        version: "2.0.4",
        creationDate: "2026-06-08",
        sampleCount: 50000,
        source: "redteam-audit-suite",
        contentHash: "sha256-ff889a72f1c8e1e786b889fa087a9f9922e4"
      },
      {
        name: "Antigravity-Temporal-Memory-Lattices",
        version: "1.1.2",
        creationDate: "2026-06-09",
        sampleCount: 25000,
        source: "memory-governors-drift-logs",
        contentHash: "sha256-b09a0a1f0a8e3d81b89fa0c8c1e828d1c9ef"
      }
    ];
  }

  getDatasets(): RegisteredDataset[] {
    return this.datasets;
  }

  getDataset(name: string): RegisteredDataset | undefined {
    return this.datasets.find(d => d.name === name);
  }
}
