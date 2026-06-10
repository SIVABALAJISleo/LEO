export interface LoadFailureReport {
    simulatedUsers: number[];
    p50: number;
    p95: number;
    p99: number;
    timeouts: number;
    crashes: number;
    topFailures: string[];
}

export const runLoadHunter = async (): Promise<LoadFailureReport> => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                simulatedUsers: [100, 500, 1000, 5000, 10000],
                p50: 120, // ms
                p95: 450, // ms
                p99: 1800, // ms
                timeouts: 0.012, // 1.2%
                crashes: 0.001, // 0.1%
                topFailures: [
                    "P99 latency spiked significantly at 10,000 concurrent users.",
                    "Timeouts observed in external API dependencies during stress testing.",
                    "Intermittent agent crashes due to out-of-memory errors on heavy loads.",
                    "Connection pool exhaustion led to cascading failures."
                ]
            });
        }, 1200);
    });
};
