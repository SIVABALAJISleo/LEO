const express = require("express");
const cors = require("cors");

const app = express();
const PORT = process.env.PORT || 8005;

app.use(cors());
app.use(express.json());

// Simple health check that your frontend hook is calling
app.get("/health", (req, res) => {
  res.json({ status: "ok", message: "Backend is running" });
});

// Example placeholder route for a “GPU job”
// Right now this just waits for a bit and returns a fake result.
// Later you (or your senior) can replace the inside with real heavy work.
app.post("/jobs", async (req, res) => {
  const { payload } = req.body || {};

  // Simulate some heavy work on CPU for now
  const start = Date.now();
  while (Date.now() - start < 500) {
    Math.sqrt(Math.random());
  }

  res.json({
    jobId: "demo-job-1",
    done: true,
    note: "This is a demo CPU-based job. Replace with real GPU logic later.",
    inputSummary: payload ?? null,
  });
});

app.listen(PORT, () => {
  console.log(`Backend server listening on http://localhost:${PORT}`);
});
