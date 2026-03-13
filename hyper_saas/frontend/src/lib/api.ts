import axios from 'axios';

export interface HyperResponse {
    status: string;
    mode: string;
    expert: string;
    result: string;
    compute_cost_avoided: boolean;
    latency_ms: number;
}

class HyperClient {
    private baseUrl = '/api/v1';

    async orchestrate(query: string): Promise<HyperResponse> {
        try {
            const response = await axios.post(`${this.baseUrl}/orchestrate`, { query });
            return response.data;
        } catch (error) {
            console.error("HyperClient error", error);
            // Client-side fallback if backend is unreachable
            return {
                status: "fallback",
                mode: "CLIENT_PREDICTION",
                expert: "Local_Engine",
                result: `Optimistic fallback for: ${query}`,
                compute_cost_avoided: true,
                latency_ms: 0
            };
        }
    }

    getOptimisticResult(query: string): string {
        return `Predicting intent for: "${query}"...`;
    }
}

export const hyperClient = new HyperClient();
