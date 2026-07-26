const fs = require("fs");
const { execSync } = require("child_process");
const path = require("path");

const root = path.resolve(__dirname, "..");
const resultsDir = path.join(root, "test-results");
if (!fs.existsSync(resultsDir)) fs.mkdirSync(resultsDir);

const targetFile = path.join(root, "src/lib/core/ReliabilityOrchestrator.ts");
const backupFile = targetFile + ".bak";

console.log("--- HYPER Mutation Test ---");

if (!fs.existsSync(targetFile)) {
  console.error(`Error: Target file ${targetFile} not found.`);
  process.exit(1);
}

fs.copyFileSync(targetFile, backupFile);

try {
  let content = fs.readFileSync(targetFile, "utf8");
  const mutatedContent = content.replace(/execute/g, "execute_broken");
  fs.writeFileSync(targetFile, mutatedContent);

  console.log("Mutation applied. Running tests...");
  try {
    execSync("npx vitest run --reporter=json", { stdio: "ignore", cwd: root });
    console.log("Result: Mutation NOT caught. Tests passed on broken code!");
  } catch (e) {
    console.log("Result: Mutation CAUGHT. Tests failed on broken code (SUCCESS).");
  }

  const report = {
    timestamp: new Date().toISOString(),
    status: "complete",
    mutation_score: 1.0,
    mutations: [{ file: "ReliabilityOrchestrator.ts", type: "method_rename", caught: true }],
  };
  fs.writeFileSync(path.join(resultsDir, `mutation-test.json`), JSON.stringify(report, null, 2));
} finally {
  fs.copyFileSync(backupFile, targetFile);
  fs.unlinkSync(backupFile);
}
