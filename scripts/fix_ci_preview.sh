#!/usr/bin/env bash
# Automated Fix Script for LEO CI Preview & SSR Failures
# Root Cause: TanStack Start + Nitro SSR requires booting .output/server/index.mjs instead of vite preview
set -euo pipefail

echo "================================================================"
echo "  HYPER / LEO — Automated CI & SSR Preview Self-Healing Script  "
echo "================================================================"

# 1. Check repo root
if [ ! -f package.json ]; then
  echo "Error: Must be run from the repository root (package.json not found)."
  exit 1
fi

# 2. Patch package.json preview script
echo "[1/4] Updating package.json preview script..."
node -e '
const fs = require("fs");
const p = JSON.parse(fs.readFileSync("package.json", "utf8"));
p.scripts.preview = "node .output/server/index.mjs";
fs.writeFileSync("package.json", JSON.stringify(p, null, 2) + "\n");
'
echo "      -> preview script set to 'node .output/server/index.mjs'"

# 3. Patch vite.config.ts to support NITRO_PRESET env override
echo "[2/4] Ensuring vite.config.ts respects NITRO_PRESET..."
node -e '
const fs = require("fs");
let cfg = fs.readFileSync("vite.config.ts", "utf8");
if (!cfg.includes("process.env.NITRO_PRESET")) {
  cfg = cfg.replace(/nitro:\s*\{\s*preset:\s*["\x27]vercel["\x27]\s*\}/g, "nitro: { preset: process.env.NITRO_PRESET || \"vercel\" }");
  fs.writeFileSync("vite.config.ts", cfg);
  echo("      -> vite.config.ts patched with process.env.NITRO_PRESET");
} else {
  console.log("      -> vite.config.ts already supports process.env.NITRO_PRESET");
}
'

# 4. Patch backend/reflect/scripts/learning_ledger.py for bandit B324
echo "[3/4] Ensuring bandit security compliance in learning_ledger.py..."
node -e '
const fs = require("fs");
const file = "backend/reflect/scripts/learning_ledger.py";
if (fs.existsSync(file)) {
  let content = fs.readFileSync(file, "utf8");
  content = content.replace(/hashlib\.md5\(f"\{fingerprint\}\{now\}"\.encode\(\)\)/g, "hashlib.md5(f\"{fingerprint}{now}\".encode(), usedforsecurity=False)");
  fs.writeFileSync(file, content);
  console.log("      -> learning_ledger.py secured with usedforsecurity=False");
}
'

# 5. Build and verify
echo "[4/4] Verifying node preset build..."
NITRO_PRESET=node npm run build || NITRO_PRESET=node bun run build

if [ -f .output/server/index.mjs ]; then
  echo "SUCCESS: .output/server/index.mjs created successfully!"
else
  echo "ERROR: .output/server/index.mjs was not produced."
  exit 1
fi

echo "================================================================"
echo "All automated fixes applied successfully!"
echo "You can now commit and push the changes:"
echo "  git add package.json vite.config.ts backend/reflect/scripts/learning_ledger.py scripts/fix_ci_preview.sh"
echo "  git commit -m \"fix(ci): support NITRO_PRESET in preview and resolve bandit security warnings\""
echo "  git push"
echo "================================================================"
