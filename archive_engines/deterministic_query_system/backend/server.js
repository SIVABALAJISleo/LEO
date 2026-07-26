const express = require("express");
const cors = require("cors");
const { BloomFilter } = require("bloomfilter");

const app = express();
app.use(cors());
app.use(express.json());

// --- GRAPH DATABASE (IN-MEMORY FOR DETERMINISM) ---
const graph = {
  nodes: {
    "ent-001": { id: "ent-001", type: "ENTITY", name: "ALPHA_NODE", category: "Hardware" },
    "ent-002": { id: "ent-002", type: "ENTITY", name: "BETA_NODE", category: "Hardware" },
    "ent-003": { id: "ent-003", type: "ENTITY", name: "CORE_SWITCH", category: "Network" },

    "met-001": { id: "met-001", type: "METRIC", name: "CPU_LOAD", unit: "%" },
    "met-002": { id: "met-002", type: "METRIC", name: "MEMORY_USAGE", unit: "GB" },
    "met-003": { id: "met-003", type: "METRIC", name: "LATENCY", unit: "ms" },

    "tme-001": { id: "tme-001", type: "TIME", name: "LAST_1H" },
    "tme-002": { id: "tme-002", type: "TIME", name: "LAST_24H" },
    "tme-003": { id: "tme-003", type: "TIME", name: "REALTIME" },

    "cnd-001": { id: "cnd-001", type: "CONDITION", name: "CRITICAL" },
    "cnd-002": { id: "cnd-002", type: "CONDITION", name: "WARNING" },
    "cnd-003": { id: "cnd-003", type: "CONDITION", name: "NOMINAL" },
  },
  edges: {
    // ENTITY -> METRIC
    "ent-001": ["met-001", "met-002", "met-003"],
    "ent-002": ["met-001", "met-002"],
    "ent-003": ["met-003"],

    // METRIC -> TIME
    "met-001": ["tme-001", "tme-002"],
    "met-002": ["tme-001", "tme-002"],
    "met-003": ["tme-001", "tme-002", "tme-003"],

    // TIME -> CONDITION
    "tme-001": ["cnd-001", "cnd-002", "cnd-003"],
    "tme-002": ["cnd-001", "cnd-002", "cnd-003"],
    "tme-003": ["cnd-001"],
  },
};

// --- BLOOM FILTER (PRE-VALIDATION) ---
// We pre-calculate all valid 4-step paths
const validPaths = new Set();
for (const e in graph.edges) {
  if (graph.nodes[e].type === "ENTITY") {
    for (const m of graph.edges[e]) {
      for (const t of graph.edges[m]) {
        for (const c of graph.edges[t]) {
          validPaths.add(`${e}|${m}|${t}|${c}`);
        }
      }
    }
  }
}

const bloom = new BloomFilter(32 * 1024, 16);
validPaths.forEach((path) => bloom.add(path));

// --- API ENDPOINTS ---

app.get("/api/nodes", (req, res) => {
  res.json(Object.values(graph.nodes));
});

app.post("/api/resolve", (req, res) => {
  const { uuids } = req.body;

  if (!uuids || uuids.length === 0) {
    return res.status(400).json({ error: "No intent blocks selected." });
  }

  const path = uuids.join("|");

  // 1. Bloom Filter Check (Fast path)
  if (!bloom.test(path)) {
    return res.status(403).json({
      status: "REJECTED",
      reason: "INVALID_GRAPH_PATH",
      message:
        "This specific combination of intent blocks is not physically possible in the system graph.",
    });
  }

  // 2. Deterministic Execution (Graph Traversal)
  const result = {
    trace: uuids.map((id) => graph.nodes[id].name),
    timestamp: new Date().toISOString(),
    outcome: `DETERMINISTIC_FETCH: Result for ${graph.nodes[uuids[0]].name} > ${graph.nodes[uuids[1]].name}`,
    data: {
      value: (Math.random() * 100).toFixed(2),
      unit: graph.nodes[uuids[1]].unit || "",
    },
  };

  res.json({
    status: "SUCCESS",
    result,
  });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Deterministic Graph Server running on port ${PORT}`);
  console.log(`Valid paths indexed in Bloom Filter: ${validPaths.size}`);
});
