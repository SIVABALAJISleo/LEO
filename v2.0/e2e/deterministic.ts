import type { Page } from "@playwright/test";

/**
 * Freeze anything non-visual that would otherwise change between runs:
 *   - Date.now() / new Date() → fixed epoch
 *   - Math.random()           → deterministic LCG
 *   - crypto.randomUUID()     → counter-based UUIDs
 *   - performance.now()       → monotonic from 0
 *   - CSS animations + transitions → disabled via <style>
 *
 * Call BEFORE `page.goto(...)` so init hooks land in the page context.
 */
export async function freezeNonVisual(
  page: Page,
  opts: { epochMs?: number } = {},
) {
  const epoch = opts.epochMs ?? Date.parse("2026-01-15T12:00:00.000Z");

  await page.addInitScript((frozenEpoch: number) => {
    // Deterministic RNG (Mulberry32).
    let seed = 0xc0ffee;
    Math.random = () => {
      seed = (seed + 0x6d2b79f5) >>> 0;
      let t = seed;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };

    // Frozen wall clock — Date.now() and `new Date()` (no args) both return
    // the frozen epoch. Date parsing / explicit args still work.
    const RealDate = Date;
    const FrozenDate = function (this: unknown, ...args: unknown[]) {
      if (args.length === 0) return new RealDate(frozenEpoch);
      // @ts-expect-error — pass through
      return new RealDate(...args);
    } as unknown as DateConstructor;
    FrozenDate.now = () => frozenEpoch;
    FrozenDate.parse = RealDate.parse;
    FrozenDate.UTC = RealDate.UTC;
    FrozenDate.prototype = RealDate.prototype;
    // @ts-expect-error — replace global Date
    globalThis.Date = FrozenDate;

    // Counter UUIDs so React keys / session ids don't drift.
    let uuidCounter = 0;
    const nextUuid = () => {
      uuidCounter += 1;
      const hex = uuidCounter.toString(16).padStart(12, "0");
      return `00000000-0000-4000-8000-${hex}`;
    };
    if (typeof crypto !== "undefined") {
      try {
        // @ts-expect-error — override
        crypto.randomUUID = nextUuid;
      } catch {
        /* readonly in some browsers — fall back to random override above */
      }
    }

    // Zero-based monotonic performance.now for stable telemetry timing.
    if (typeof performance !== "undefined") {
      const start = performance.now();
      const orig = performance.now.bind(performance);
      performance.now = () => Math.round(orig() - start);
    }

    // Inject an animation-off stylesheet as early as possible.
    const disableAnim = () => {
      const style = document.createElement("style");
      style.setAttribute("data-testid", "deterministic-anim-off");
      style.textContent = `
        *, *::before, *::after {
          animation-duration: 0ms !important;
          animation-delay: 0ms !important;
          transition-duration: 0ms !important;
          transition-delay: 0ms !important;
          caret-color: transparent !important;
        }
      `;
      (document.head || document.documentElement).appendChild(style);
    };
    if (document.readyState !== "loading") disableAnim();
    else document.addEventListener("DOMContentLoaded", disableAnim, { once: true });
  }, epoch);
}
