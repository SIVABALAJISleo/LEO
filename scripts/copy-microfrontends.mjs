import fs from "node:fs";
import path from "node:path";

const src = "microfrontends.json";
const targets = [
  path.join(".vercel", "output", "microfrontends.json"),
  path.join(".vercel", "output", "static", "microfrontends.json"),
  path.join(".output", "microfrontends.json"),
  path.join(".output", "public", "microfrontends.json"),
  path.join("public", "microfrontends.json"),
  path.join("dist", "microfrontends.json"),
  path.join("dist", "client", "microfrontends.json"),
];

if (fs.existsSync(src)) {
  for (const target of targets) {
    const dir = path.dirname(target);
    try {
      fs.mkdirSync(dir, { recursive: true });
      fs.copyFileSync(src, target);
      console.log(`[mfe] Copied ${src} -> ${target}`);
    } catch (err) {
      console.warn(`[mfe] Could not copy to ${target}:`, err.message);
    }
  }
}
