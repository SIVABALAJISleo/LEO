import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 100 }, // Ramp up to 100 users
    { duration: "1m", target: 500 }, // Spike to 500 users
    { duration: "1m", target: 1000 }, // Spike to 1,000 users
    { duration: "30s", target: 0 }, // Ramp down to 0
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"], // 95% of requests must complete within 500ms
    http_req_failed: ["rate<0.01"], // Error rate must be less than 1%
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export default function () {
  // Test Health & Observability Metrics
  const metricsRes = http.get(`${BASE_URL}/api/v1/leo/metrics`);
  check(metricsRes, {
    "metrics status is 200": (r) => r.status === 200,
  });

  // Test Memory Query
  const payload = JSON.stringify({ query: "Enterprise compliance benchmark" });
  const params = { headers: { "Content-Type": "application/json" } };
  const queryRes = http.post(`${BASE_URL}/api/v1/v40/memory/query`, payload, params);
  check(queryRes, {
    "memory query status is 200 or 404": (r) => r.status === 200 || r.status === 404,
  });

  sleep(1);
}
