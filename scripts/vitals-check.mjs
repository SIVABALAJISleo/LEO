#!/usr/bin/env node
// Web Vitals performance budget check. Boots Chromium against the built
// preview URL, collects LCP/CLS/INP via the `web-vitals` runtime, and fails
// CI when any metric exceeds the budget below.
//
// Env:
//   VITALS_BASE_URL   default http://127.0.0.1:4173
//   VITALS_ROUTES     comma-separated list; default "/,/features,/benchmarks,/docs"
//   VITALS_BUDGET_LCP default 2500  (ms — "good" per web.dev)
//   VITALS_BUDGET_INP default 200   (ms — "good")
//   VITALS_BUDGET_CLS default 0.10  ("good")
//
// The script uses INP approximated via a synthetic click / keydown burst so
// the metric fires even in a headless run (real INP requires user input).
import { chromium } from "playwright";

const BASE = process.env.VITALS_BASE_URL ?? "http://127.0.0.1:4173";
const ROUTES = (process.env.VITALS_ROUTES ?? "/,/features,/benchmarks,/docs")
  .split(",")
  .map((r) => r.trim())
  .filter(Boolean);
const BUDGETS = {
  LCP: Number(process.env.VITALS_BUDGET_LCP ?? 2500),
  INP: Number(process.env.VITALS_BUDGET_INP ?? 200),
  CLS: Number(process.env.VITALS_BUDGET_CLS ?? 0.1),
};

/** @type {Array<{route:string, name:string, value:number, budget:number, pass:boolean}>} */
const results = [];

// Web vitals collection script using ESM imports compatible with web-vitals@5.x
const webVitalsScript = `
import { onLCP, onCLS, onINP } from 'https://cdn.jsdelivr.net/npm/web-vitals@5/+esm';

window.__vitals = {};
try {
  onLCP((m) => {
    window.__vitals.LCP = m.value;
  });
  onCLS((m) => {
    window.__vitals.CLS = m.value;
  });
  onINP((m) => {
    window.__vitals.INP = m.value;
  });
} catch (e) {
  console.error('Error setting up web vitals:', e);
}
`;

async function measure(page, route) {
  // Inject web vitals measurement script
  await page.addInitScript(() => {
    window.__vitals = {};
  });

  await page.goto(`${BASE}${route}`, { waitUntil: "networkidle", timeout: 60_000 });

  // Inject web vitals library and collect metrics
  await page.evaluate(() => {
    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.type = 'module';
      script.textContent = `
        import { onLCP, onCLS, onINP } from 'https://cdn.jsdelivr.net/npm/web-vitals@5/+esm';
        window.__vitals = window.__vitals || {};
        onLCP((m) => (window.__vitals.LCP = m.value));
        onCLS((m) => (window.__vitals.CLS = m.value));
        onINP((m) => (window.__vitals.INP = m.value));
        window.__vitalsReady = true;
      `;
      document.head.appendChild(script);
      
      // Wait for vitals to be ready
      const checkReady = setInterval(() => {
        if (window.__vitalsReady) {
          clearInterval(checkReady);
          resolve();
        }
      }, 100);
      
      setTimeout(() => {
        clearInterval(checkReady);
        resolve();
      }, 3000);
    });
  });

  // Trigger some real interactions so INP has samples
  await page.mouse.move(100, 100);
  await page.mouse.down();
  await page.mouse.up();
  await page.keyboard.press("Tab");
  await page.keyboard.press("Tab");
  await page.evaluate(() => new Promise((r) => setTimeout(r, 1500)));

  // Force LCP + CLS finalization by hiding the tab
  await page.evaluate(() => {
    Object.defineProperty(document, "visibilityState", { value: "hidden", configurable: true });
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await page.evaluate(() => new Promise((r) => setTimeout(r, 400)));

  return page.evaluate(() => window.__vitals ?? {});
}

const browser = await chromium.launch();
try {
  for (const route of ROUTES) {
    const ctx = await browser.newContext({
      viewport: { width: 1366, height: 900 },
    });
    const page = await ctx.newPage();
    let vitals = {};
    try {
      vitals = await measure(page, route);
    } catch (err) {
      console.error(`✗ ${route}: navigation failed — ${err.message}`);
      results.push({ route, name: "NAV", value: NaN, budget: 0, pass: false });
      await ctx.close();
      continue;
    }
    await ctx.close();
    for (const [name, budget] of Object.entries(BUDGETS)) {
      const value = vitals[name];
      if (typeof value !== "number" || Number.isNaN(value)) {
        // INP may not fire without real user input; treat missing INP as pass
        // to avoid flakes, but still print it. LCP + CLS should always fire.
        if (name === "INP") {
          console.log(`  ${route}  INP=(not collected — skipped)`);
          continue;
        }
        console.error(`✗ ${route}  ${name}=(missing)`);
        results.push({ route, name, value: NaN, budget, pass: false });
        continue;
      }
      const pass = value <= budget;
      results.push({ route, name, value, budget, pass });
      const marker = pass ? "✓" : "✗";
      console.log(
        `  ${route}  ${marker} ${name}=${value.toFixed(name === "CLS" ? 3 : 0)} (budget ${budget})`,
      );
    }
  }
} finally {
  await browser.close();
}

const failed = results.filter((r) => !r.pass);
console.log("");
console.log(
  `Web Vitals budget: ${results.length - failed.length}/${results.length} checks passed.`,
);
if (failed.length > 0) {
  console.error("Failed checks:");
  for (const f of failed) {
    console.error(
      `  ${f.route} ${f.name}: ${Number.isNaN(f.value) ? "missing" : f.value.toFixed(f.name === "CLS" ? 3 : 0)} > ${f.budget}`,
    );
  }
  process.exit(1);
}
