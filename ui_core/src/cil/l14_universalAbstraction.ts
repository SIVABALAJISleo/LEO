/**
 * Layer 14: Universal Abstraction Layer
 * Purpose: Future-proof the architecture by designing all systems around generic interfaces.
 */

export interface ICognitiveNode {
  id: string;
  capabilities: string[];
  process(input: ICognitivePayload): Promise<ICognitivePayload>;
}

export interface ICognitivePayload {
  semanticContent: any;
  confidence: number;
  metadata: Record<string, any>;
  provenance: string[];
}

export interface IHardwareAdapter {
  targetArchitecture:
    "Transformers" | "Mamba" | "RWKV" | "MoE" | "Neuromorphic" | "Quantum" | "Unknown";
  execute(payload: ICognitivePayload): Promise<ICognitivePayload>;
}

export class UniversalAbstractionLayer {
  /**
   * Wraps any incoming computation request to ensure it conforms to the CIL standard.
   */
  public wrapRequest(content: any): ICognitivePayload {
    return {
      semanticContent: content,
      confidence: 1.0,
      metadata: { timestamp: Date.now() },
      provenance: ["USER_INPUT"],
    };
  }
}
