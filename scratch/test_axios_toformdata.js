import toFormData from "../node_modules/axios/lib/helpers/toFormData.js";

console.log("======================================================");
console.log("   LEO SECURITY AUDIT — AXIOS toFormData DoS (CVE)");
console.log("======================================================");

import axios from "axios";
console.log("Active Axios Version:", axios.VERSION);

function nest(depth) {
  let o = { leaf: 1 };
  for (let i = 0; i < depth; i++) o = { a: o };
  return o;
}

let passed = 0;
let failed = 0;

function test(label, fn, expectError) {
  try {
    fn();
    if (expectError) {
      console.log(`  [FAILED] ${label.padEnd(45)} -> No error thrown! VULNERABLE.`);
      failed++;
    } else {
      console.log(`  [SAFE]   ${label.padEnd(45)} -> Accepted (shallow input).`);
      passed++;
    }
  } catch (e) {
    if (expectError) {
      const tag = e.code === "ERR_FORM_DATA_DEPTH_EXCEEDED" ? "Depth guard" : e.name;
      console.log(`  [SAFE]   ${label.padEnd(45)} -> Blocked: ${tag}`);
      passed++;
    } else {
      console.log(`  [FAILED] ${label.padEnd(45)} -> Rejected clean input: ${e.message}`);
      failed++;
    }
  }
}

console.log("\n-- ATTACK VECTORS (must be BLOCKED) --");
test("depth=2500 (PoC from advisory)", () => toFormData(nest(2500)), true);
test("depth=500", () => toFormData(nest(500)), true);
test("depth=150", () => toFormData(nest(150)), true);

console.log("\n-- CLEAN INPUTS (must be ACCEPTED) --");
test("depth=5 (normal payload)", () => toFormData(nest(5)), false);
test("depth=50", () => toFormData(nest(50)), false);
test("flat object {a:1, b:2}", () => toFormData({ a: 1, b: 2 }), false);

console.log("\n======================================================");
const total = passed + failed;
if (failed === 0) {
  console.log(`  AUDIT PASSED: ${passed}/${total} checks secure. toFormData DoS mitigated.`);
  process.exit(0);
} else {
  console.log(`  AUDIT FAILED: ${failed}/${total} checks vulnerable!`);
  process.exit(1);
}
