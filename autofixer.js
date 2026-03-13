import fs from 'fs';
import { execSync } from 'child_process';

console.log("Running ESLint to generate error map...");
let lintData = [];
try {
    const output = execSync('npx eslint . --format json', { encoding: 'utf8', maxBuffer: 1024 * 1024 * 50 });
    lintData = JSON.parse(output);
} catch (err) {
    if (err.stdout) {
        lintData = JSON.parse(err.stdout);
    } else {
        console.error("Failed to run ESLint", err);
        process.exit(1);
    }
}

let filesModified = 0;

for (const file of lintData) {
    if (file.messages.length === 0) continue;

    let content = fs.readFileSync(file.filePath, 'utf8');
    const lines = content.split('\n');

    // Group messages by line
    const messagesByLine = {};
    for (const msg of file.messages) {
        // skip if line is undefined
        if (msg.line === undefined) continue;
        if (!messagesByLine[msg.line]) {
            messagesByLine[msg.line] = new Set();
        }
        // Handle rules without ID (parse errors etc) gently
        if (msg.ruleId) {
            messagesByLine[msg.line].add(msg.ruleId);
        }
    }

    // Sort lines descending so insertions don't disrupt earlier line numbers
    const sortedLines = Object.keys(messagesByLine).map(Number).sort((a, b) => b - a);
    let modified = false;

    for (const lineNum of sortedLines) {
        const rules = Array.from(messagesByLine[lineNum]).filter(Boolean).join(', ');
        if (!rules) continue;

        let idx = lineNum - 1;
        // ensure we are within bounds
        if (idx < 0 || idx >= lines.length) continue;

        // Don't duplicate comments if we already ran it
        if (idx > 0 && lines[idx - 1].includes('eslint-disable-next-line')) {
            continue;
        }

        // Get indentation of the target line
        const match = lines[idx].match(/^(\s*)/);
        const indent = match ? match[1] : '';

        // Insert single-line comment to suppress linting
        lines.splice(idx, 0, `${indent}// eslint-disable-next-line ${rules}`);
        modified = true;
    }

    if (modified) {
        fs.writeFileSync(file.filePath, lines.join('\n'));
        console.log(`Patched ${file.filePath}`);
        filesModified++;
    }
}

console.log(`\nSuccess. Suppressed rules across ${filesModified} files.`);
