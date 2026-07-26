// V29 — Phase 2 Delta World Update Engine
// Updates only changes in state, avoiding total reconstructions of semantic parameters

import { TopologicalWorldModel, TopologicalNode } from "./topologicalWorldModel";

export interface WorldDelta {
  nodeId: string;
  fieldChanged: string;
  oldValue: any;
  newValue: any;
  timestamp: number;
}

export class DeltaWorldUpdateEngine {
  private deltaLog: WorldDelta[] = [];

  applyUpdates(
    model: TopologicalWorldModel,
    observations: { nodeId: string; properties: Record<string, any> }[],
  ): WorldDelta[] {
    const freshDeltas: WorldDelta[] = [];

    observations.forEach((obs) => {
      const node = model.getNode(obs.nodeId);
      if (node) {
        Object.entries(obs.properties).forEach(([key, val]) => {
          const oldVal = node.properties[key];
          if (JSON.stringify(oldVal) !== JSON.stringify(val)) {
            // Log changes
            const delta: WorldDelta = {
              nodeId: obs.nodeId,
              fieldChanged: key,
              oldValue: oldVal,
              newValue: val,
              timestamp: Date.now(),
            };
            node.properties[key] = val;
            this.deltaLog.push(delta);
            freshDeltas.push(delta);
          }
        });
      }
    });

    return freshDeltas;
  }

  getDeltaLog(): WorldDelta[] {
    return this.deltaLog;
  }
}
