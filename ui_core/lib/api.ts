import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8005/api/v1";

export const leoApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export interface LeoStatus {
  status: string;
  system: string;
  layers: number;
  telemetry: any;
  semantic_store_size: number;
  fingerprint_store_size: number;
  timestamp: number;
}

export interface OrchestrateRequest {
  query: string;
  workspace_id?: string;
  quality_hint?: string;
}

export interface LayerTrace {
  layer_id: number;
  layer_name: string;
  resolved: boolean;
  confidence: number;
  latency_ms: number;
}

export interface OrchestrateResponse {
  result: string;
  answer: string;
  resolved_by: string;
  latency_ms: number;
  confidence: number;
  compute_avoided: boolean;
  gpu_watts_saved: number;
  entropy_tier: string;
  layer_trace: LayerTrace[];
  trace: {
    resolved_by_layer: string;
    total_latency_ms: number;
  };
}

export const fetchLeoStatus = async (): Promise<LeoStatus> => {
  const res = await leoApi.get("/leo/status");
  return res.data;
};

export const simulateQuery = async (req: OrchestrateRequest): Promise<OrchestrateResponse> => {
  const res = await leoApi.post("/leo/orchestrate", req);
  return res.data;
};
