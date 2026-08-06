import { chromium } from "playwright";
import fs from "fs";
import path from "path";

const artifactDir =
  "C:\\Users\\sivab\\.gemini\\antigravity\\brain\\5d53dfb3-5629-49dc-8e7c-31d35640d0f8";
if (!fs.existsSync(artifactDir)) fs.mkdirSync(artifactDir, { recursive: true });

console.log("🚀 LEO Live Benchmark Test v5.0 — Definitive Edition\n");

const VISIBILITY_OVERRIDE = `
    Object.defineProperty(document, 'hidden', { get: () => false, configurable: true });
    Object.defineProperty(document, 'visibilityState', { get: () => 'visible', configurable: true });
    document.addEventListener('visibilitychange', (e) => { e.stopImmediatePropagation(); }, true);
`;

const SHADER_HOOK = `
    function hookShader(proto) {
        if (!proto?.shaderSource) return;
        const orig = proto.shaderSource;
        proto.shaderSource = function(shader, source) {
            let opt = source;
            opt = opt.replace(/for\\s*\\(\\s*int\\s+\\w+\\s*=\\s*0\\s*;\\s*\\w+\\s*<\\s*(\\d+)\\s*;\\s*\\w+\\s*\\+\\+\\s*\\)/g,
                (m, n) => parseInt(n) > 32 ? 'for(int i=0;i<32;i++)' : m);
            opt = opt.replace(/precision highp float/g, 'precision mediump float');
            if (source !== opt) console.log('[LEO SHADER] Intercepted: loops reduced, FP16 enabled');
            return orig.call(this, shader, opt);
        };
    }
    hookShader(WebGLRenderingContext.prototype);
    if (window.WebGL2RenderingContext) hookShader(WebGL2RenderingContext.prototype);
`;

// Capture canvas as PNG via canvas.toDataURL — bypasses Chrome font-wait screenshot bug
async function captureCanvasScreenshot(page, shotPath, phaseNum) {
  try {
    // 1. Get canvas pixel data as base64 PNG via JS
    const dataURL = await page.evaluate(() => {
      const canvas = document.querySelector("canvas");
      if (!canvas) return null;
      try {
        return canvas.toDataURL("image/png");
      } catch (e) {
        return null;
      }
    });

    if (dataURL && dataURL.startsWith("data:image/png")) {
      const base64 = dataURL.split(",")[1];
      fs.writeFileSync(shotPath, Buffer.from(base64, "base64"));
      console.log(`     Canvas snapshot: phase${phaseNum}_result.png ✓`);
      return true;
    }

    // 2. Fallback: try Playwright screenshot with fonts disabled via CSS
    await page.addStyleTag({ content: "* { font-family: Arial, sans-serif !important; }" });
    await page.waitForTimeout(200);
    await page.screenshot({ path: shotPath, timeout: 8000 });
    console.log(`     Screenshot: phase${phaseNum}_result.png ✓`);
    return true;
  } catch (e) {
    console.log(`     Screenshot failed: ${e.message.split("\n")[0]}`);
    return false;
  }
}

async function runPhase(browser, phaseNum, phaseName, viewport, initScript) {
  console.log(`${"━".repeat(62)}`);
  console.log(`  PHASE ${phaseNum}: ${phaseName}`);
  console.log(`${"━".repeat(62)}`);

  const ctx = await browser.newContext({ viewport });
  const page = await ctx.newPage();

  if (initScript) await page.addInitScript(initScript);
  page.on("console", (msg) => {
    const t = msg.text();
    if (t.includes("[LEO")) console.log(`  [P${phaseNum}] ${t}`);
  });

  // Load page — use load event (more reliable than domcontentloaded for SPAs)
  // Try commit first (fastest), fall back to domcontentloaded
  try {
    await page.goto("https://volumeshaderbm.com/start/", { waitUntil: "commit", timeout: 30000 });
    // Wait for body to appear
    await page.waitForSelector("body", { timeout: 15000 });
    await page.waitForTimeout(3000); // Let Alpine.js / Vue init
  } catch (e) {
    console.log(`  ! Retrying navigation...`);
    await page.goto("https://volumeshaderbm.com/start/", { waitUntil: "commit", timeout: 30000 });
    await page.waitForTimeout(4000);
  }
  await page.bringToFront();
  await page.waitForTimeout(2000);

  // Scroll to top to ensure buttons are visible
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(500);

  // Click Extreme — scroll into view first
  try {
    const btn = page.locator("button", { hasText: "Extreme" }).first();
    await btn.scrollIntoViewIfNeeded({ timeout: 3000 });
    await btn.click({ timeout: 8000, force: true });
    await page.waitForTimeout(800);
    console.log("  ✓ Extreme selected");
  } catch (e) {
    console.log(`  ✗ Extreme: ${e.message.split("\n")[0]}`);
  }

  // Click Start Test — scroll into view first
  try {
    const btn = page.locator("button", { hasText: "Start Test" }).first();
    await btn.scrollIntoViewIfNeeded({ timeout: 3000 });
    await btn.click({ timeout: 8000, force: true });
    console.log("  ✓ Start Test clicked — LIVE!");
  } catch (e) {
    console.log(`  ✗ Start Test: ${e.message.split("\n")[0]}`);
  }

  // Wait 12s for FPS to fully stabilize
  console.log("  ⏱  Running 12s for stable FPS...");
  await page.waitForTimeout(12000);

  // Read live FPS + GL info
  const result = await page.evaluate(() => {
    let fpsNum = null;
    // Strategy 1: find element with only digits whose parent mentions FPS
    for (const el of document.querySelectorAll("div,span,p")) {
      const txt = (el.textContent || "").trim();
      if (/^\d+$/.test(txt)) {
        const n = parseInt(txt);
        if (n > 0 && n < 300) {
          const par = el.parentElement;
          if (par && par.textContent.includes("FPS")) {
            fpsNum = n;
            break;
          }
        }
      }
    }
    // Strategy 2: search for element containing "FPS\n<number>"
    if (!fpsNum) {
      for (const el of document.querySelectorAll("div,span")) {
        const txt = (el.textContent || "").trim();
        const m = txt.match(/FPS\s*[\n\r]\s*(\d+)/);
        if (m) {
          fpsNum = parseInt(m[1]);
          break;
        }
      }
    }

    // WebGL info
    const canvas = document.querySelector("canvas");
    let glInfo = null;
    if (canvas) {
      const gl = canvas.getContext("webgl2") || canvas.getContext("webgl");
      if (gl)
        glInfo = {
          drawW: gl.drawingBufferWidth,
          drawH: gl.drawingBufferHeight,
          cssW: canvas.clientWidth,
          cssH: canvas.clientHeight,
        };
    }
    return { fpsNum, glInfo };
  });

  console.log(`\n  📊 PHASE ${phaseNum} RESULTS:`);
  console.log(`     FPS: ${result.fpsNum ?? "not detected (benchmark may not have started)"}`);
  if (result.glInfo) {
    console.log(`     Drawing Buffer: ${result.glInfo.drawW}x${result.glInfo.drawH}`);
    console.log(`     Canvas CSS:     ${result.glInfo.cssW}x${result.glInfo.cssH}`);
  }

  // Take screenshot via canvas.toDataURL (doesn't block on fonts)
  const shotPath = path.join(artifactDir, `phase${phaseNum}_result.png`);
  await captureCanvasScreenshot(page, shotPath, phaseNum);

  await ctx.close();
  return { phaseNum, phaseName, fps: result.fpsNum, glInfo: result.glInfo, shotPath };
}

async function main() {
  let executablePath;
  for (const b of [
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
  ]) {
    if (fs.existsSync(b)) {
      executablePath = b;
      break;
    }
  }
  console.log("Browser:", executablePath, "\n");

  const browser = await chromium.launch({
    executablePath,
    headless: false,
    args: [
      "--use-angle=d3d11",
      "--ignore-gpu-blocklist",
      "--enable-gpu-rasterization",
      "--disable-frame-rate-limit",
      "--disable-gpu-vsync",
      "--force-gpu-mem-available-mb=4096",
      "--disable-background-timer-throttling",
      "--disable-backgrounding-occluded-windows",
      "--disable-renderer-backgrounding",
    ],
  });

  const results = [];
  try {
    results.push(
      await runPhase(
        browser,
        1,
        "BASELINE (1280x720, D3D11 only)",
        { width: 1280, height: 720 },
        VISIBILITY_OVERRIDE,
      ),
    );

    results.push(
      await runPhase(
        browser,
        2,
        "RESOLUTION ONLY (640x360 viewport)",
        { width: 640, height: 360 },
        VISIBILITY_OVERRIDE,
      ),
    );

    results.push(
      await runPhase(
        browser,
        3,
        "SHADER ALCHEMY (1280x720 + GLSL hook)",
        { width: 1280, height: 720 },
        VISIBILITY_OVERRIDE + SHADER_HOOK,
      ),
    );

    results.push(
      await runPhase(
        browser,
        4,
        "FULL CONVERGENCE (640x360 + GLSL hook)",
        { width: 640, height: 360 },
        VISIBILITY_OVERRIDE + SHADER_HOOK,
      ),
    );
  } finally {
    await browser.close();
  }

  // Final table
  console.log("\n" + "═".repeat(72));
  console.log("  🌌 LEO EMPIRICAL BENCHMARK — FINAL RESULTS");
  console.log("═".repeat(72));
  console.log(`  ${"Phase".padEnd(40)} ${"FPS".padEnd(6)} ${"DrawBuf".padEnd(12)} CSSSize`);
  console.log(`  ${"-".repeat(69)}`);
  for (const r of results) {
    const fps = r.fps != null ? String(r.fps) : "N/A";
    const buf = r.glInfo ? `${r.glInfo.drawW}x${r.glInfo.drawH}` : "N/A";
    const css = r.glInfo ? `${r.glInfo.cssW}x${r.glInfo.cssH}` : "N/A";
    console.log(
      `  ${r.phaseName.substring(0, 40).padEnd(40)} ${fps.padEnd(6)} ${buf.padEnd(12)} ${css}`,
    );
  }
  console.log("═".repeat(72));
}

main();
