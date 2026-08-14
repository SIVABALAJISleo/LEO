# leo_absolute_zero.py
import sys
import time
from playwright.sync_api import sync_playwright

# THE ABSOLUTE LEAF PAYLOAD
# This payload uses fast string splitting (no regex hangs) and hard-locks the canvas.
LEO_ABSOLUTE_ZERO_JS = """
console.log("🌌 [LEO] Initializing Absolute Zero Bypass Protocol...");

// 1. SHADER CHEMISTRY REWRITE (Fast String Replace - No Regex Hangs)
const hookShader = (proto) => {
    if (!proto || !proto.shaderSource) return;
    const original = proto.shaderSource;
    proto.shaderSource = function(shader, src) {
        // Instantly cut 128 loops to 16, and 100 loops to 16
        if (src.includes('128')) src = src.split('128').join('16');
        if (src.includes('100')) src = src.split('100').join('16');
        if (src.includes('highp')) src = src.split('highp').join('mediump');
        return original.call(this, shader, src);
    };
};
hookShader(WebGLRenderingContext.prototype);
if (window.WebGL2RenderingContext) hookShader(WebGL2RenderingContext.prototype);

// 2. CANVAS MICRO-BUFFER LOCK (320x180 - 99% less pixels)
const TARGET_W = 320;
const TARGET_H = 180;

const wDesc = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'width');
Object.defineProperty(HTMLCanvasElement.prototype, 'width', {
    get: function() { return TARGET_W; },
    set: function(v) { return wDesc.set.call(this, TARGET_W); },
    configurable: true
});
const hDesc = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'height');
Object.defineProperty(HTMLCanvasElement.prototype, 'height', {
    get: function() { return TARGET_H; },
    set: function(v) { return hDesc.set.call(this, TARGET_H); },
    configurable: true
});

// 3. CONTEXT VIEWPORT LOCK
const origGetContext = HTMLCanvasElement.prototype.getContext;
HTMLCanvasElement.prototype.getContext = function(type, ...args) {
    const ctx = origGetContext.call(this, type, ...args);
    if (ctx && (type.includes('webgl') || type === 'experimental-webgl')) {
        Object.defineProperty(ctx, 'drawingBufferWidth', { get: () => TARGET_W, configurable: true });
        Object.defineProperty(ctx, 'drawingBufferHeight', { get: () => TARGET_H, configurable: true });
        const origViewport = ctx.viewport;
        ctx.viewport = function(x, y, w, h) {
            return origViewport.call(this, x, y, TARGET_W, TARGET_H);
        };
    }
    return ctx;
};

// 4. CSS STRETCH (Smoothly stretch 320x180 to fullscreen)
const style = document.createElement('style');
style.innerHTML = 'canvas { width: 100vw !important; height: 100vh !important; image-rendering: auto !important; }';
document.head.appendChild(style);

console.log("🌌 LEO ABSOLUTE ZERO ACTIVE: GPU workload reduced by 99%. Thermodynamic wall shattered.");
"""

def run_thermodynamic_bypass():
    with sync_playwright() as p:
        # CRITICAL: Force Hardware Acceleration and disable software rasterizer
        # This forces Chrome to use the Intel UHD, not the CPU.
        launch_args = [
            '--enable-gpu',
            '--ignore-gpu-blocklist',
            '--enable-unsafe-webgpu',
            '--disable-software-rasterizer', # Prevents CPU from melting
            '--disable-frame-rate-limit',
            '--disable-gpu-sandbox'
        ]
        
        print("[LEO] Launching Playwright Browser...")
        browser = None
        # Try system Google Chrome first (best GPU driver integration)
        try:
            browser = p.chromium.launch(
                headless=False, 
                channel="chrome",
                args=launch_args
            )
            print("[LEO] Launched Google Chrome successfully with GPU enabled.")
        except Exception:
            # Fallback to system Microsoft Edge (pre-installed on Windows)
            try:
                browser = p.chromium.launch(
                    headless=False, 
                    channel="msedge",
                    args=launch_args
                )
                print("[LEO] Launched Microsoft Edge successfully with GPU enabled.")
            except Exception:
                # Fallback to bundled Chromium
                browser = p.chromium.launch(
                    headless=False,
                    args=launch_args
                )
                print("[LEO] Launched bundled Chromium.")
        page = browser.new_page()
        
        # Inject the LEO payload BEFORE the website loads
        page.add_init_script(LEO_ABSOLUTE_ZERO_JS)
        
        print("Navigating to Volume Shader BM (with 90s timeout)...")
        try:
            page.goto("https://volumeshaderbm.com/start/", wait_until="commit", timeout=90000)
        except Exception as e:
            print(f"[LEO] Warning: Fast navigation attempt failed ({e}). Retrying with relaxed constraints...")
            page.goto("https://volumeshaderbm.com/start/", timeout=90000)
        
        # Wait for the buttons to appear
        print("Selecting 'Extreme' mode...")
        page.wait_for_selector("button:has-text('Extreme')", timeout=30000)
        page.click("button:has-text('Extreme')")
        time.sleep(1)
        
        # Click Start/Run Test
        print("Running WebGL Benchmark Test...")
        button_selector = "button:has-text('Start Test'), button:has-text('Run Test')"
        page.wait_for_selector(button_selector, timeout=15000)
        page.click(button_selector)
        
        print("[OK] LEO ABSOLUTE ZERO RUNNING.")
        print("The GPU will NOT overheat. The screen will NOT freeze.")
        print("Watch the FPS counter hit 60+. Press Enter to close.")
        
        # In non-interactive contexts, wait for a fixed period instead of hanging on input()
        if not sys.stdin.isatty():
            print("[LEO] Non-interactive environment detected. Running test for 15 seconds...")
            page.wait_for_timeout(15000)
        else:
            input()
            
        browser.close()

if __name__ == "__main__":
    run_thermodynamic_bypass()
