#!/usr/bin/env node
import fs from "node:fs";
import { execSync } from "node:child_process";

console.log("================================================================");
console.log("  HYPER / LEO — Automated CI & SSR Preview Self-Healing Script  ");
console.log("================================================================");

// 1. Check repo root
if (!fs.existsSync("package.json")) {
  console.error("Error: Must be run from the repository root (package.json not found).");
  process.exit(1);
}

// 2. Patch package.json preview script
console.log("[1/3] Updating package.json preview script...");
const pkg = JSON.parse(fs.readFileSync("package.json", "utf8"));
pkg.scripts.preview = "node .output/server/index.mjs";
fs.writeFileSync("package.json", JSON.stringify(pkg, null, 2) + "\n");
console.log("      -> preview script set to 'node .output/server/index.mjs'");

// 3. Patch vite.config.ts to support NITRO_PRESET env override
console.log("[2/3] Ensuring vite.config.ts respects NITRO_PRESET...");
let cfg = fs.readFileSync("vite.config.ts", "utf8");
if (!cfg.includes("process.env.NITRO_PRESET")) {
  cfg = cfg.replace(
    /nitro:\s*\{\s*preset:\s*["']vercel["']\s*\}/g,
    'nitro: { preset: process.env.NITRO_PRESET || "vercel" }',
  );
  fs.writeFileSync("vite.config.ts", cfg);
  console.log("      -> vite.config.ts patched with process.env.NITRO_PRESET");
} else {
  console.log("      -> vite.config.ts already supports process.env.NITRO_PRESET");
}

// 4. Patch backend/reflect/scripts/learning_ledger.py for bandit B324
console.log("[3/3] Ensuring bandit security compliance in learning_ledger.py...");
const ledgerFile = "backend/reflect/scripts/learning_ledger.py";
if (fs.existsSync(ledgerFile)) {
  let content = fs.readFileSync(ledgerFile, "utf8");
  content = content.replace(
    /hashlib\.md5\(f"\{fingerprint\}\{now\}"\.encode\(\)\)/g,
    'hashlib.md5(f"{fingerprint}{now}".encode(), usedforsecurity=False)',
  );
  fs.writeFileSync(ledgerFile, content);
  console.log("      -> learning_ledger.py secured with usedforsecurity=False");
}

console.log("\n================================================================");
console.log("All automated fixes applied successfully!");
console.log("You can commit and push the changes with:");
console.log("  git add package.json vite.config.ts backend/reflect/scripts/learning_ledger.py");
console.log(
  '  git commit -m "fix(ci): support NITRO_PRESET in preview and resolve bandit security warnings"',
);
console.log("  git push");
console.log("================================================================");
