# leo_process_governor.py
# LEO v6 Process Governor
# Prevents the browser from overheating the CPU by enforcing process priority limits.
# Run this in the background WHILE running any benchmark or heavy browser task.

import sys
import time

# Configure stdout to use UTF-8 to prevent UnicodeEncodeError on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Auto-install psutil if missing
try:
    import psutil
except ModuleNotFoundError:
    import subprocess
    print("[LEO] psutil not found. Auto-installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True)
    import psutil

# ─── Configuration ───────────────────────────────────────────────────────────
BROWSER_NAMES   = ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"]
POLL_INTERVAL   = 1.0    # How often to check processes (seconds)
CPU_WARN_THRESH = 80.0   # Log a warning if any browser process exceeds this %
# ─────────────────────────────────────────────────────────────────────────────

def get_browser_processes():
    procs = []
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['name'] and p.info['name'].lower() in BROWSER_NAMES:
                procs.append(p)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return procs

def set_below_normal(p):
    """Set process priority to Below Normal. Returns True if changed."""
    try:
        current = p.nice()
        # On Windows: BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
        # psutil maps it to psutil.BELOW_NORMAL_PRIORITY_CLASS
        target = psutil.BELOW_NORMAL_PRIORITY_CLASS
        if current != target:
            p.nice(target)
            return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return False

def restore_normal(procs):
    """Restore all governed processes to Normal priority on exit."""
    for p in procs:
        try:
            p.nice(psutil.NORMAL_PRIORITY_CLASS)
            print(f"[LEO] Restored {p.info['name']} (PID {p.pid}) to Normal priority.")
        except Exception:
            pass

print("=" * 55)
print("  LEO v6 PROCESS GOVERNOR — Thermal Frame Pacer")
print("=" * 55)
print("Strategy : Limit browser CPU priority -> prevent 100% spikes")
print("Target   : Smooth 60 FPS with zero thermal throttling")
print("Watching :", ", ".join(BROWSER_NAMES))
print("-" * 55)
print("Press Ctrl+C to stop and restore normal priority.\n")

governed_pids = set()

try:
    while True:
        browser_procs = get_browser_processes()

        for p in browser_procs:
            try:
                changed = set_below_normal(p)
                if changed and p.pid not in governed_pids:
                    governed_pids.add(p.pid)
                    print(f"[{time.strftime('%H:%M:%S')}] Governed  {p.info['name']:20s} PID {p.pid} -> Below Normal priority")

                # CPU usage warning
                cpu_pct = p.cpu_percent(interval=None)
                if cpu_pct > CPU_WARN_THRESH:
                    print(f"[{time.strftime('%H:%M:%S')}] WARNING   {p.info['name']:20s} PID {p.pid} CPU={cpu_pct:.1f}% (above {CPU_WARN_THRESH}%)")

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                governed_pids.discard(p.pid if hasattr(p, 'pid') else 0)

        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("\n[LEO] Ctrl+C received. Restoring browser priorities...")
    restore_normal(get_browser_processes())
    print("[LEO] Governor stopped cleanly. Your benchmark is now unlocked.")
