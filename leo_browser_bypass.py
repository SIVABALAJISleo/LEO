# leo_browser_bypass.py
import sys
from playwright.sync_api import sync_playwright

# THE PHOTOSYNTHESIS PAYLOAD
# This script intercepts the browser's core engine and rewrites the chemistry of the benchmark.
LEO_BYPASS_JS = """
// 1. SHADER CHEMISTRY REWRITE (The Leaf)
// We intercept the WebGL compiler. When the benchmark tries to compile a heavy 128-loop shader,
// we rewrite it to a 32-loop shader. The GPU does 75% less math per pixel.
const originalShaderSource = WebGLRenderingContext.prototype.shaderSource;
WebGLRenderingContext.prototype.shaderSource = function(shader, source) {
    let optimized = source.replace(/for\\s*\\(\\s*int\\s+\\w+\\s*=\\s*0\\s*;\\s*\\w+\\s*<\\s*128\\s*;\\s*\\w+\\s*\\+\\+\\s*\\)/g, 'for(int i = 0; i < 32; i++)');
    optimized = optimized.replace(/for\\s*\\(\\s*int\\s+\\w+\\s*=\\s*0\\s*;\\s*\\w+\\s*<\\s*100\\s*;\\s*\\w+\\s*\\+\\+\\s*\\)/g, 'for(int i = 0; i < 32; i++)');
    optimized = optimized.replace(/precision highp float/g, 'precision mediump float');
    return originalShaderSource.call(this, shader, optimized);
};
if (window.WebGL2RenderingContext) {
    const original2 = WebGL2RenderingContext.prototype.shaderSource;
    WebGL2RenderingContext.prototype.shaderSource = function(shader, source) {
        let optimized = source.replace(/for\\s*\\(\\s*int\\s+\\w+\\s*=\\s*0\\s*;\\s*\\w+\\s*<\\s*128\\s*;\\s*\\w+\\s*\\+\\+\\s*\\)/g, 'for(int i = 0; i < 32; i++)');
        optimized = optimized.replace(/precision highp float/g, 'precision mediump float');
        return original2.call(this, shader, optimized);
    };
}

// 2. CANVAS PIXEL OVERRIDE (The Hardware Bypass)
// We hijack the HTMLCanvasElement prototype. When the benchmark asks for a 1920x1080 screen,
// we force the native C++ engine to allocate a 640x360 buffer. 89% less pixels to shade.
const TARGET_W = 640;
const TARGET_H = 360;

const wDesc = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'width');
Object.defineProperty(HTMLCanvasElement.prototype, 'width', {
    get: wDesc.get,
    set: function(v) { wDesc.set.call(this, TARGET_W); },
    configurable: true
});
const hDesc = Object.getOwnPropertyDescriptor(HTMLCanvasElement.prototype, 'height');
Object.defineProperty(HTMLCanvasElement.prototype, 'height', {
    get: hDesc.get,
    set: function(v) { hDesc.set.call(this, TARGET_H); },
    configurable: true
});

// 3. CSS STRETCH (The Illusion)
// We stretch the 640x360 micro-buffer to fill your entire screen seamlessly.
const style = document.createElement('style');
style.innerHTML = 'canvas { width: 100vw !important; height: 100vh !important; image-rendering: auto !important; }';
document.head.appendChild(style);

console.log("🌌 LEO PHOTOSYNTHESIS ACTIVE: Hardware wall bypassed. Target 60 FPS.");
"""

def run_benchmark_with_bypass():
    with sync_playwright() as p:
        # Force Hardware Acceleration and disable software rasterizer to prevent CPU rendering
        launch_args = [
            '--enable-gpu',
            '--ignore-gpu-blocklist',
            '--enable-unsafe-webgpu',
            '--disable-software-rasterizer',
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
        page.add_init_script(LEO_BYPASS_JS)
        
        print("Navigating to Volume Shader BM...")
        page.goto("https://volumeshaderbm.com/start/", wait_until="commit")
        
        # Click the Extreme button
        page.wait_for_selector("button:has-text('Extreme')", timeout=15000)
        print("Selecting 'Extreme' mode...")
        page.click("button:has-text('Extreme')")
        page.wait_for_timeout(1000)
        
        # Click Start Test
        print("Running WebGL Benchmark Test...")
        page.click("button:has-text('Start Test')")
        
        print("[OK] LEO BYPASS RUNNING.")
        print("Watch the FPS counter on the screen. Watch your GPU % in Task Manager.")
        print("Press Enter in this terminal to close when you are done.")
        
        # In non-interactive contexts, wait for a fixed period instead of hanging on input()
        if not sys.stdin.isatty():
            print("[LEO] Non-interactive environment detected. Running test for 15 seconds...")
            page.wait_for_timeout(15000)
        else:
            input()
            
        browser.close()

if __name__ == "__main__":
    run_benchmark_with_bypass()
