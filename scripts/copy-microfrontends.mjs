import fs from "node:fs";
import path from "node:path";

const src = "microfrontends.json";
const targets = [
  path.join(".vercel", "output", "microfrontends.json"),
  path.join(".vercel", "output", "static", "microfrontends.json"),
  path.join(".output", "microfrontends.json"),
];

if (fs.existsSync(src)) {
  for (const target of targets) {
    const dir = path.dirname(target);
    if (fs.existsSync(dir)) {
      fs.copyFileSync(src, target);
      console.log(`[mfe] Copied ${src} -> ${target}`);
    }
  }
}

