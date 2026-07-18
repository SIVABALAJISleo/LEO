# LEO AI V45 COMPLETENESS AUDIT TEST PLAN

This plan defines the end-to-end test cases evaluated by the local multi-agent testing team. Every test case is mapped to a unique ID.

---

## 1. Frontend UI/UX (FE)

- **FE-001: Dashboard Navigation & Tab Switching**
  - *Goal:* Verify all dashboard tabs render correctly. Select and active tab `v45singularity`.
  - *Expected:* Renders the V45 Singularity Dashboard interface with a particle canvas.
- **FE-002: Bandwidth Formula Slider Interaction**
  - *Goal:* Drag sliders for Ternary, Speculative depth, iGPU, and CAT L3 cache.
  - *Expected:* Dynamically computes and displays the correct virtual bandwidth value.
- **FE-003: LEO Assistant Toggle & Chat Drawer**
  - *Goal:* Click the Assistant button to open the chat window.
  - *Expected:* Opens the drawer sidebar, triggers health queries to the backend, and displays connectivity status.

---

## 2. Backend APIs (BE)

- **BE-001: System Status endpoint**
  - *Goal:* `GET http://localhost:8005/api/v1/leo/status`
  - *Expected:* Status code 200, status = "OK", returns request metrics.
- **BE-002: Hardware Profile endpoint**
  - *Goal:* `GET http://localhost:8005/api/v1/leo/hardware`
  - *Expected:* Status code 200, parses CPU/iGPU specifications.
- **BE-003: Resource Telemetry endpoint**
  - *Goal:* `GET http://localhost:8005/api/v1/compute/telemetry`
  - *Expected:* Status code 200, returns active CPU/RAM usage bounds.
- **BE-004: Query Orchestration POST endpoint**
  - *Goal:* `POST http://localhost:8005/api/v1/leo/orchestrate` with payload `{"query": "hello"}`
  - *Expected:* Status code 200, runs query trace and returns output text.

---

## 3. Database Integrity (DB)

- **DB-001: Crystallization Read/Write Persistence**
  - *Goal:* Query `crystallized_answers` table in `hyper_engine.db`.
  - *Expected:* Select queries execute successfully, verifying schemas and hit counters.
- **DB-002: Cache Storage Budget Limit**
  - *Goal:* Check cache directory size constraints.
  - *Expected:* Enforces budget bounds under 500MB, deleting oldest cached keys if exceeded.

---

## 4. Security (SEC)

- **SEC-001: Middleware Guardrails & Headers**
  - *Goal:* Inspect response headers and payload size boundaries.
  - *Expected:* Content-Security-Policy header is active; POST requests exceeding 5MB are terminated.

---

## 5. Performance (PERF)

- **PERF-001: Warm Cache Latency Bound**
  - *Goal:* Execute a cached query resonance lookup.
  - *Expected:* Latency remains under the **5 ms** target boundary.
- **PERF-002: Virtual Memory Space Headroom**
  - *Goal:* Query system RAM capacity.
  - *Expected:* System RAM utilization leaves at least 1.0 GB free to prevent swap storms.

---

## 6. Integration (INT)

- **INT-001: UI/API Contract Mapping**
  - *Goal:* Validate if Frontend displays VSA hit rate metrics parsed from Backend Status responses.
  - *Expected:* UI renders the correct hit percentage corresponding to the API.
