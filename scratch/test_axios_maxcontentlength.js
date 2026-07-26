import http from "http";
import axios from "axios";

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS Stream maxContentLength");
console.log("======================================================");
console.log("Active Axios Version:", axios.VERSION);

// Start local test server
const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "application/octet-stream" });
  // Send 100KB of data
  res.write(Buffer.alloc(100 * 1024, "a"));
  res.end();
});

server.listen(0, "127.0.0.1", async () => {
  const port = server.address().port;
  let passed = 0;
  let failed = 0;

  async function test(label, maxContentLength, expectBlocked) {
    try {
      const response = await axios.get(`http://127.0.0.1:${port}/`, {
        responseType: "stream",
        maxContentLength,
      });

      // Consume the stream fully
      let receivedBytes = 0;
      for await (const chunk of response.data) {
        receivedBytes += chunk.length;
      }

      if (expectBlocked) {
        console.log(
          `  [FAILED] ${label.padEnd(50)} -> Read fully (${receivedBytes} bytes). VULNERABLE.`,
        );
        failed++;
      } else {
        console.log(`  [SAFE]   ${label.padEnd(50)} -> Completed successfully (Expected).`);
        passed++;
      }
    } catch (e) {
      if (expectBlocked) {
        const errorMsg = e.message;
        console.log(`  [SAFE]   ${label.padEnd(50)} -> Blocked: ${errorMsg}`);
        passed++;
      } else {
        console.log(`  [FAILED] ${label.padEnd(50)} -> Failed unexpectedly: ${e.message}`);
        failed++;
      }
    }
  }

  try {
    console.log("\n-- TESTING INBOUND LIMIT ENFORCEMENT --");

    // 1. MaxContentLength = 10KB (limit breached)
    await test("Stream response with maxContentLength=10KB", 10 * 1024, true);

    // 2. MaxContentLength = 200KB (limit not breached)
    await test("Stream response with maxContentLength=200KB", 200 * 1024, false);

    console.log("\n======================================================");
    const total = passed + failed;
    if (failed === 0) {
      console.log(
        `  AUDIT PASSED: ${passed}/${total} checks secure. maxContentLength stream bypass mitigated.`,
      );
      process.exit(0);
    } else {
      console.log(`  AUDIT FAILED: ${failed}/${total} checks vulnerable!`);
      process.exit(1);
    }
  } catch (err) {
    console.error("Test framework error:", err);
    process.exit(1);
  } finally {
    server.close();
  }
});
