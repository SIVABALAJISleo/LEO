import axios from 'axios';
import mergeConfig from '../node_modules/axios/lib/core/mergeConfig.js';

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS validateStatus PE");
console.log("======================================================");
console.log("Active Axios Version:", axios.VERSION);

let passed = 0;
let failed = 0;

function runTest(testName, config1, config2, expectDefaultCheck) {
  const merged = mergeConfig(config1, config2);
  const validator = merged.validateStatus;
  
  if (expectDefaultCheck) {
    // Default validateStatus should reject 401/500 and accept 200
    const accepts200 = validator ? validator(200) : false;
    const accepts401 = validator ? validator(401) : false;
    const accepts500 = validator ? validator(500) : false;
    
    if (accepts200 && !accepts401 && !accepts500) {
      console.log(`  [SAFE]   ${testName.padEnd(50)} -> Default behavior preserved.`);
      passed++;
    } else {
      console.log(`  [FAILED] ${testName.padEnd(50)} -> Default behavior compromised! (200:${accepts200}, 401:${accepts401}, 500:${accepts500})`);
      failed++;
    }
  } else {
    // If we passed custom validator, it should be honored
    const accepts401 = validator ? validator(401) : false;
    if (accepts401) {
      console.log(`  [SAFE]   ${testName.padEnd(50)} -> Custom status validator honored.`);
      passed++;
    } else {
      console.log(`  [FAILED] ${testName.padEnd(50)} -> Custom status validator lost.`);
      failed++;
    }
  }
}

try {
  // 1. Clean state check
  console.log("\n-- TESTING NORMAL BEHAVIOR (no prototype pollution) --");
  runTest("Default validateStatus merge", { validateStatus: axios.defaults.validateStatus }, {}, true);
  runTest("Custom validateStatus override", { validateStatus: axios.defaults.validateStatus }, { validateStatus: () => true }, false);

  // 2. Pollute Object.prototype
  console.log("\n-- TESTING PROTOTYPE POLLUTION ATTACK --");
  console.log("Polluting Object.prototype.validateStatus with () => true...");
  Object.prototype.validateStatus = () => true;

  // With the vulnerability, merging an empty config would copy the polluted validateStatus
  // and accept all status codes (including 401/500).
  runTest("Default merge under active prototype pollution", { validateStatus: axios.defaults.validateStatus }, {}, true);
  
  // Clean up prototype pollution
  delete Object.prototype.validateStatus;

  console.log("\n======================================================");
  const total = passed + failed;
  if (failed === 0) {
    console.log(`  AUDIT PASSED: ${passed}/${total} checks secure. validateStatus PP bypass mitigated.`);
    process.exit(0);
  } else {
    console.log(`  AUDIT FAILED: ${failed}/${total} checks vulnerable!`);
    process.exit(1);
  }
} catch (err) {
  console.error("Test framework error:", err);
  process.exit(1);
}
