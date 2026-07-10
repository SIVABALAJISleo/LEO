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

export const simulateVInfinityQuery = async (req: OrchestrateRequest): Promise<any> => {
  const res = await leoApi.post("/leo/vinfinity/orchestrate", req);
  return res.data;
};

export const runVInfinityBenchmark = async (): Promise<any> => {
  const res = await leoApi.post("/leo/vinfinity/benchmark");
  return res.data;
};

export const triggerVInfinityEvolution = async (): Promise<any> => {
  const res = await leoApi.post("/leo/vinfinity/evolve");
  return res.data;
};

export const fetchEvolutionHistory = async (): Promise<any> => {
  const res = await leoApi.get("/leo/vinfinity/evolution/history");
  return res.data;
};

export const submitTelemetry = async (entry: {
  prompt_class: string;
  latency_ms: number;
  was_avoided: boolean;
  hardware_hash?: string;
}): Promise<any> => {
  const res = await leoApi.post("/leo/vinfinity/telemetry", entry);
  return res.data;
};

export const fetchHardwareSummary = async (): Promise<any> => {
  const res = await leoApi.get("/leo/hardware");
  return res.data;
};

export const fetchSwarmStatus = async (): Promise<any[]> => {
  const res = await leoApi.get("/leo/swarm");
  return res.data;
};

export interface DevOpsSettings {
  sentry_dsn?: string;
  pagerduty_integration_key?: string;
  stripe_signature_checking?: boolean;
  canary_deployment_pct?: number;
  active_rollback?: boolean;
}

export const fetchDevOpsStatus = async (): Promise<DevOpsSettings> => {
  const res = await leoApi.get("/devops/status");
  return res.data;
};

export const configureDevOps = async (settings: DevOpsSettings): Promise<DevOpsSettings> => {
  const res = await leoApi.post("/devops/configure", settings);
  return res.data.settings;
};

export const sendStripeWebhook = async (payload: any, signature: string): Promise<any> => {
  const res = await leoApi.post("/billing/webhook", payload, {
    headers: {
      "stripe-signature": signature,
    },
  });
  return res.data;
};

export const fetchPoiLedger = async (): Promise<any> => {
  const res = await leoApi.get("/leo/v44/poi/ledger");
  return res.data;
};

export const verifySeal = async (signature: string): Promise<any> => {
  const res = await leoApi.get("/leo/v44/poi/verify", { params: { signature } });
  return res.data;
};

