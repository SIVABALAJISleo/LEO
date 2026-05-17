import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const targetFile = path.resolve(__dirname, '../node_modules/axios/lib/helpers/isURLSameOrigin.js');
const originalContent = fs.readFileSync(targetFile, 'utf8');

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS withXSRFToken LEAK");
console.log("======================================================");

try {
  // 1. Temporarily patch isURLSameOrigin to return false (always cross-origin for this test)
  console.log("Applying temporary test mock to isURLSameOrigin.js...");
  fs.writeFileSync(targetFile, "export default () => false;\n", 'utf8');

  // 2. Import modules
  const { default: axios } = await import('axios');
  const { default: resolveConfig } = await import('../node_modules/axios/lib/helpers/resolveConfig.js');
  const { default: cookies } = await import('../node_modules/axios/lib/helpers/cookies.js');
  const { default: platform } = await import('../node_modules/axios/lib/platform/index.js');

  console.log("Active Axios Version:", axios.VERSION);

  // Mock standard browser environment so XSRF logic executes
  platform.hasStandardBrowserEnv = true;
  cookies.read = () => 'mock-secret-xsrf-token';

  let passed = 0;
  let failed = 0;

  function runTest(testName, config, expectedHeaderPresent) {
    const resolved = resolveConfig({
      xsrfHeaderName: 'X-XSRF-TOKEN',
      xsrfCookieName: 'XSRF-TOKEN',
      url: 'https://attacker-origin.com/steal', // cross-origin destination
      ...config
    });
    
    const hasHeader = resolved.headers && resolved.headers.has('X-XSRF-TOKEN');
    
    if (hasHeader === expectedHeaderPresent) {
      console.log(`  [SAFE]   ${testName.padEnd(50)} -> Correct behavior.`);
      passed++;
    } else {
      console.log(`  [FAILED] ${testName.padEnd(50)} -> VULNERABLE! Header leak state: ${hasHeader}`);
      failed++;
    }
  }

  // A. Normal Behavior Checks
  console.log("\n-- TESTING NORMAL BEHAVIOR (no prototype pollution) --");
  runTest("withXSRFToken: undefined (same-origin check)", {}, false); // should not send cross-origin
  runTest("withXSRFToken: true (explicit opt-in)", { withXSRFToken: true }, true);
  runTest("withXSRFToken: false (explicit opt-out)", { withXSRFToken: false }, false);

  // B. Misconfiguration checks (truthy non-booleans)
  console.log("\n-- TESTING MISCONFIGURATIONS (truthy non-booleans) --");
  runTest("withXSRFToken: 'false' (string)", { withXSRFToken: 'false' }, false);
  runTest("withXSRFToken: 1 (number)", { withXSRFToken: 1 }, false);
  runTest("withXSRFToken: {} (object)", { withXSRFToken: {} }, false);

  // C. Prototype Pollution Attack simulation
  console.log("\n-- TESTING PROTOTYPE POLLUTION ATTACKS --");
  Object.prototype.withXSRFToken = 1; // Attempt to pollute prototype
  runTest("withXSRFToken polluted with '1'", {}, false);

  Object.prototype.withXSRFToken = true; // Attempt to pollute with true
  runTest("withXSRFToken polluted with 'true'", {}, false);

  // Clean up prototype pollution
  delete Object.prototype.withXSRFToken;

  console.log("\n======================================================");
  const total = passed + failed;
  if (failed === 0) {
    console.log(`  AUDIT PASSED: ${passed}/${total} checks secure. XSRF leakage mitigated.`);
    process.exit(0);
  } else {
    console.log(`  AUDIT FAILED: ${failed}/${total} checks vulnerable!`);
    process.exit(1);
  }
} catch (err) {
  console.error("Error during test execution:", err);
  process.exit(1);
} finally {
  // 3. Always restore the original content of isURLSameOrigin.js
  console.log("Restoring original isURLSameOrigin.js...");
  fs.writeFileSync(targetFile, originalContent, 'utf8');
}
