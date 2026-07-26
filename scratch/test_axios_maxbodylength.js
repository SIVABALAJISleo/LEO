import http from "http";
import axios from "axios";
import { Readable } from "stream";

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS Stream maxBodyLength");
console.log("======================================================");
console.log("Active Axios Version:", axios.VERSION);

// Start local test server
let receivedBytes = 0;
const server = http.createServer((req, res) => {
  req.on("data", (chunk) => {
    receivedBytes += chunk.length;
  });
  req.on("end", () => {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ received: receivedBytes }));
  });
});

server.listen(0, "127.0.0.1", async () => {
  const port = server.address().port;
  let passed = 0;
  let failed = 0;

  function createStream(size) {
    let sent = 0;
    return new Readable({
      read(chunkSize) {
        if (sent >= size) {
          this.push(null);
          return;
        }
        const toSend = Math.min(chunkSize, size - sent);
        this.push(Buffer.alloc(toSend, "a"));
        sent += toSend;
      },
    });
  }

  async function test(label, size, maxBodyLength, maxRedirects, expectBlocked) {
    receivedBytes = 0;
    const uploadStream = createStream(size);

    try {
      await axios.post(`http://127.0.0.1:${port}/`, uploadStream, {
        maxBodyLength,
        maxRedirects,
        headers: { "Content-Type": "application/octet-stream" },
      });

      if (expectBlocked) {
        console.log(
          `  [FAILED] ${label.padEnd(50)} -> Completed! (Received ${receivedBytes} bytes). VULNERABLE.`,
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
    console.log("\n-- TESTING OUTBOUND LIMIT ENFORCEMENT --");

    // Size = 100KB, maxBodyLength = 10KB, maxRedirects = 0 (Attacker vector)
    await test(
      "Stream 100KB with maxBodyLength=10KB, maxRedirects=0",
      100 * 1024,
      10 * 1024,
      0,
      true,
    );

    // Size = 5KB, maxBodyLength = 10KB, maxRedirects = 0 (Normal stream)
    await test("Stream 5KB with maxBodyLength=10KB, maxRedirects=0", 5 * 1024, 10 * 1024, 0, false);

    // Size = 100KB, maxBodyLength = 10KB, default redirects (Control check)
    await test(
      "Stream 100KB with maxBodyLength=10KB, default redirects",
      100 * 1024,
      10 * 1024,
      undefined,
      true,
    );

    console.log("\n======================================================");
    const total = passed + failed;
    if (failed === 0) {
      console.log(
        `  AUDIT PASSED: ${passed}/${total} checks secure. maxBodyLength bypass mitigated.`,
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
