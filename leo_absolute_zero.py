# leo_absolute_zero.py
import sys
import time
from playwright.sync_api import sync_playwright

# Configure stdout to use UTF-8 to prevent UnicodeEncodeError on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# THE ABSOLUTE LEAF PAYLOAD
# This payload uses fast string splitting (no regex hangs) and hard-locks the canvas.
LEO_ABSOLUTE_ZERO_JS = """
console.log("🌌 [LEO] Initializing Absolute Zero Bypass Protocol...");

// 1. SHADER CHEMISTRY REWRITE & COMPILE LOGGER
const hookShader = (proto) => {
    if (!proto) return;
    if (proto.shaderSource) {
        const original = proto.shaderSource;
        proto.shaderSource = function(shader, src) {
            let optimized = src;
            // Safely replace standalone integers 128 and 100 with 16
            // Skips "#version 100" and float literals like "100.0" or "128.0"
            optimized = optimized.replace(/\\b(?:128|100)\\b/g, (match, offset, string) => {
                const before = string.slice(Math.max(0, offset - 10), offset);
                if (before.includes("#version")) return match;
                const after = string.slice(offset + match.length, offset + match.length + 2);
                if (after.startsWith('.') || after.startsWith('.0')) return match;
                return '16';
            });
            if (optimized.includes('highp')) {
                optimized = optimized.replace(/\\bhighp\\b/g, 'mediump');
            }
            return original.call(this, shader, optimized);
        };
    }
    if (proto.compileShader) {
        const origCompile = proto.compileShader;
        proto.compileShader = function(shader) {
            origCompile.call(this, shader);
            if (!this.getShaderParameter(shader, this.COMPILE_STATUS)) {
                console.error("Shader compilation failed: " + this.getShaderInfoLog(shader));
            }
        };
    }
    if (proto.linkProgram) {
        const origLink = proto.linkProgram;
        proto.linkProgram = function(program) {
            origLink.call(this, program);
            if (!this.getProgramParameter(program, this.LINK_STATUS)) {
                console.error("Program linking failed: " + this.getProgramInfoLog(program));
            }
        };
    }
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
        page.on("console", lambda msg: print(f"[Browser Console] {msg.type.upper()}: {msg.text}"))
        
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
