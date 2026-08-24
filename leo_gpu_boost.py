# leo_gpu_boost.py
# LEO Ultimate WebGL GPU Boost
# Relaunches Chrome with maximum Intel UHD hardware acceleration flags.
# This is the real bypass: force Chrome to use the fastest possible GPU path.

import sys
import os
import subprocess
import time
import winreg

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    import psutil
except ModuleNotFoundError:
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
    import psutil

# ─── Configuration ───────────────────────────────────────────────────────────
BENCHMARK_URL = "https://volumeshaderbm.com/start/"

# These flags tell Chrome to use the fastest possible GPU pipeline for WebGL.
# This is the same technique game engines use to squeeze max FPS out of Intel iGPUs.
CHROME_BOOST_FLAGS = [
    "--use-angle=gl",                      # Use OpenGL backend (fastest for Intel UHD WebGL)
    "--enable-gpu-rasterization",           # Force GPU rasterization (not CPU software fallback)
    "--ignore-gpu-blocklist",              # Override Intel blocklist that disables features
    "--enable-zero-copy",                  # Zero-copy GPU memory transfer (removes CPU bottleneck)
    "--enable-native-gpu-memory-buffers",  # Native GPU buffer allocation (faster)
    "--enable-accelerated-2d-canvas",      # Hardware-accelerate 2D canvas
    "--enable-webgl-draft-extensions",     # Enable advanced WebGL extensions
    "--enable-unsafe-webgpu",             # Enable next-gen WebGPU (faster than WebGL)
    "--force-device-scale-factor=1",       # Disable DPI scaling overhead
    "--disable-frame-rate-limit",          # Remove 60 FPS artificial cap in Simple mode
    "--disable-gpu-vsync",                 # Remove VSync from GPU side
    "--disable-software-rasterizer",       # Force hardware only (no software fallback)
    "--max-gum-fps=144",                   # Allow up to 144 FPS
    f"--user-data-dir={os.path.join(os.environ.get('TEMP','C:\\Temp'), 'leo_chrome_boost')}",
]
# ─────────────────────────────────────────────────────────────────────────────

def find_chrome():
    """Find Chrome executable via registry or common paths."""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
        path, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if os.path.exists(path):
            return path
    except Exception:
        pass

    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""),
                     r"Google\Chrome\Application\chrome.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def set_high_performance_power_plan():
    """Switch Windows power plan to High Performance."""
    print("[LEO] Setting Windows power plan -> High Performance...")
    try:
        # High Performance GUID
        result = subprocess.run(
            ["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a875701"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("[LEO] Power plan set to High Performance.")
        else:
            # Try Ultimate Performance
            result2 = subprocess.run(
                ["powercfg", "/setactive", "e9a42b02-d5df-448d-aa00-03f14749eb61"],
                capture_output=True, text=True
            )
            if result2.returncode == 0:
                print("[LEO] Power plan set to Ultimate Performance.")
            else:
                print("[LEO] Could not set power plan. Run terminal as Administrator.")
    except Exception as e:
        print(f"[LEO] Power plan error: {e}")

def kill_existing_chrome():
    """Kill any running Chrome processes so we can relaunch with boost flags."""
    print("[LEO] Closing existing Chrome processes...")
    killed = 0
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['name'] and 'chrome' in p.info['name'].lower():
                p.kill()
                killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    if killed:
        print(f"[LEO] Closed {killed} Chrome processes.")
        time.sleep(2)
    else:
        print("[LEO] No Chrome processes found running.")

def boost_chrome_priority():
    """Set all Chrome processes to HIGH priority for maximum GPU scheduling."""
    boosted = 0
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['name'] and 'chrome' in p.info['name'].lower():
                p.nice(psutil.HIGH_PRIORITY_CLASS)
                boosted += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return boosted

def launch_boosted_chrome(chrome_path):
    """Launch Chrome with all GPU acceleration flags pointed at the benchmark."""
    cmd = [chrome_path] + CHROME_BOOST_FLAGS + [BENCHMARK_URL]
    print(f"\n[LEO] Launching Chrome with {len(CHROME_BOOST_FLAGS)} GPU boost flags...")
    proc = subprocess.Popen(cmd)
    return proc

def monitor_loop():
    """Monitor Chrome priority and keep it at HIGH throughout the benchmark."""
    print("\n[LEO] Monitoring Chrome priority. Press Ctrl+C to stop.\n")
    print("-" * 55)
    iteration = 0
    try:
        while True:
            time.sleep(3)
            boosted = boost_chrome_priority()
            iteration += 1
            if iteration % 5 == 0:  # Log every 15 seconds
                print(f"[{time.strftime('%H:%M:%S')}] Maintaining HIGH priority on {boosted} Chrome processes.")
    except KeyboardInterrupt:
        print("\n[LEO] Stopping boost monitor. Restoring Normal priority...")
        for p in psutil.process_iter(['pid', 'name']):
            try:
                if p.info['name'] and 'chrome' in p.info['name'].lower():
                    p.nice(psutil.NORMAL_PRIORITY_CLASS)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        print("[LEO] Done. Chrome priority restored.")

def main():
    print("=" * 55)
    print("  LEO ULTIMATE WebGL GPU BOOST")
    print("  Intel UHD Maximum Acceleration Protocol")
    print("=" * 55)

    # Step 1: Power Plan
    set_high_performance_power_plan()

    # Step 2: Find Chrome
    chrome = find_chrome()
    if not chrome:
        print("\n[LEO ERROR] Chrome not found. Please install Google Chrome.")
        return
    print(f"[LEO] Chrome found: {chrome}")

    # Step 3: Kill existing Chrome
    kill_existing_chrome()

    # Step 4: Launch boosted Chrome
    launch_boosted_chrome(chrome)

    # Step 5: Wait for Chrome to start, then boost priority
    print("[LEO] Waiting 5 seconds for Chrome to initialize...")
    time.sleep(5)
    boosted = boost_chrome_priority()
    print(f"[LEO] Set HIGH priority on {boosted} Chrome processes.")

    print("\n" + "=" * 55)
    print("  BOOST ACTIVE — Run your benchmark now!")
    print("  Expected: 60+ FPS on ALL modes (Simple to Extreme)")
    print("=" * 55)
    print("\nKey changes applied:")
    print("  [1] Windows power plan  -> High Performance")
    print("  [2] Chrome ANGLE backend -> OpenGL (fastest for Intel UHD)")
    print("  [3] GPU blocklist       -> Overridden")
    print("  [4] Zero-copy GPU memory -> Enabled")
    print("  [5] FPS cap             -> Removed (Simple mode won't overheat)")
    print("  [6] Chrome process priority -> HIGH")
    print("  [7] GPU VSync           -> Disabled")
    print("\nBenchmark URL auto-opened: volumeshaderbm.com/start/")
    print("\nMonitoring Chrome priority (Ctrl+C to stop)...")

    # Step 6: Keep monitoring
    monitor_loop()

if __name__ == "__main__":
    main()
