/**
 * src/services/api/contract.ts
 * Typed API Client for LEO Quantum Backend APIs
 */
import axios, { AxiosInstance } from "axios";

export interface KGQueryResult {
  entities: Array<{ id: string; label: string; type: string }>;
  relations: Array<{ source: string; target: string; relationship: string }>;
  query_time_ms: number;
}

export interface MemoryItem {
  id: string;
  key: string;
  value: string;
  category: string;
  timestamp: string;
}

export interface CascadeQueryResponse {
  response: string;
  chosen_expert: string;
  compute_avoided: boolean;
  latency_ms: number;
}

export class LEOApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = "http://localhost:8005") {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem("leo_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Knowledge Graph APIs
  async getKnowledgeGraph(query: string): Promise<KGQueryResult> {
    const response = await this.client.get("/api/v1/leo/kg/query", { params: { q: query } });
    return response.data;
  }

  // Memory System APIs
  async getMemories(type?: string): Promise<MemoryItem[]> {
    const response = await this.client.get("/api/v1/leo/memory", { params: { type } });
    return response.data;
  }

  async addMemory(memory: Partial<MemoryItem>): Promise<MemoryItem> {
    const response = await this.client.post("/api/v1/leo/memory", memory);
    return response.data;
  }

  // Model Cascade APIs
  async queryModel(prompt: string): Promise<CascadeQueryResponse> {
    const response = await this.client.post("/v1/chat/completions", {
      messages: [{ role: "user", content: prompt }],
    });
    return response.data;
  }

  // Benchmarking APIs
  async getBenchmarks(): Promise<any> {
    const response = await this.client.get("/api/v1/scoreboard");
    return response.data;
  }

  // Swarm Mesh APIs
  async getSwarmStatus(): Promise<any> {
    const response = await this.client.get("/api/v1/leo/swarm");
    return response.data;
  }
}

export const leoApi = new LEOApiClient();
