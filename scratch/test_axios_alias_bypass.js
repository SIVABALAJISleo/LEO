import http from "http";
import axios from "axios";
import shouldBypassProxy from "../node_modules/axios/lib/helpers/shouldBypassProxy.js";

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS no_proxy ALIAS BYPASS");
console.log("======================================================");
console.log("Active Axios Version:", axios.VERSION);

let passed = 0;
let failed = 0;

function runTest(testName, noProxyValue, requestUrl, shouldBypass) {
  process.env.NO_PROXY = noProxyValue;
  const bypassed = shouldBypassProxy(requestUrl);

  if (bypassed === shouldBypass) {
    console.log(`  [SAFE]   ${testName.padEnd(55)} -> Correct behavior.`);
    passed++;
  } else {
    console.log(
      `  [FAILED] ${testName.padEnd(55)} -> VULNERABLE! (Expected bypass: ${shouldBypass}, got: ${bypassed})`,
    );
    failed++;
  }
}

// Ensure NO_PROXY is cleared
delete process.env.no_proxy;
delete process.env.NO_PROXY;

console.log("\n-- TESTING no_proxy=localhost --");
runTest("Request to http://localhost/ (match)", "localhost", "http://localhost/", true);
runTest(
  "Request to http://127.0.0.1/ (IPv4 loopback alias)",
  "localhost",
  "http://127.0.0.1/",
  true,
);
runTest("Request to http://[::1]/ (IPv6 loopback alias)", "localhost", "http://[::1]/", true);

console.log("\n-- TESTING no_proxy=127.0.0.1 --");
runTest("Request to http://127.0.0.1/ (match)", "127.0.0.1", "http://127.0.0.1/", true);
runTest("Request to http://localhost/ (alias)", "127.0.0.1", "http://localhost/", true);
runTest("Request to http://[::1]/ (alias)", "127.0.0.1", "http://[::1]/", true);

console.log("\n-- TESTING no_proxy=::1 --");
runTest("Request to http://[::1]/ (match)", "::1", "http://[::1]/", true);
runTest("Request to http://localhost/ (alias)", "::1", "http://localhost/", true);
runTest("Request to http://127.0.0.1/ (alias)", "::1", "http://127.0.0.1/", true);

console.log("\n-- NEGATIVE TESTS --");
runTest("Request to external domain (should proxy)", "localhost", "http://example.com/", false);
runTest(
  "Request to internal non-loopback (should proxy)",
  "localhost",
  "http://192.168.1.5/",
  false,
);

console.log("\n======================================================");
const total = passed + failed;
if (failed === 0) {
  console.log(`  AUDIT PASSED: ${passed}/${total} checks secure. Alias bypass mitigated.`);
  process.exit(0);
} else {
  console.log(`  AUDIT FAILED: ${failed}/${total} checks vulnerable!`);
  process.exit(1);
}
