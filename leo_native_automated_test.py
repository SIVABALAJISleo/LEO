# leo_native_automated_test.py
import sys
import os
import subprocess
import time

# Configure stdout to use UTF-8 to prevent UnicodeEncodeError on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Auto-install dependencies if missing
required_packages = {
    "pyautogui": "pyautogui"
}

for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
    except ModuleNotFoundError:
        print(f"[LEO] Dependency '{package_name}' is missing. Auto-installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)
            print(f"[LEO] Successfully installed {package_name}.")
        except Exception as e:
            print(f"[LEO] Error installing {package_name}: {e}. Please run: pip install {package_name}")
    except ImportError as e:
        print(f"[LEO] Error importing {module_name}: {e}")

try:
    import pyautogui
except ImportError:
    pass

class LEODeepScanAutopilot:
    def __init__(self):
        print("🌌 Initializing LEO Deep Scan Autopilot (Photosynthesis Mode)...")
        print("Scanning system drives for 3D engines...")
        self.blender_path = self._deep_search("blender.exe")
        if not self.blender_path:
            self.blender_path = self._find_blender_appx()
        self.unity_path = self._deep_search("Unity.exe")
        self.unreal_path = self._deep_search("UnrealEditor.exe")

    def _find_blender_appx(self):
        print("   -> Querying Windows AppX database for Microsoft Store Blender...")
        try:
            cmd = ["powershell", "-Command", "Get-AppxPackage -Name '*blender*' | Select-Object -ExpandProperty InstallLocation"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            install_dir = res.stdout.strip()
            if install_dir and os.path.exists(install_dir):
                candidate = os.path.join(install_dir, "Blender", "blender.exe")
                if os.path.exists(candidate):
                    print(f"      [FOUND via AppX] blender.exe -> {candidate}")
                    return candidate
        except Exception:
            pass
        return None

    def _deep_search(self, filename):
        # Search common locations deeply (specific subdirectories first to optimize speed)
        search_roots = [
            r"C:\Program Files\Blender Foundation",
            r"C:\Program Files\Unity\Hub\Editor",
            r"C:\Program Files\Unity",
            r"C:\Program Files\Epic Games",
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Downloads")
        ]
        
        for root_dir in search_roots:
            if not os.path.exists(root_dir): continue
            print(f"   -> Scanning {root_dir}...")
            for root, dirs, files in os.walk(root_dir):
                # Limit depth to prevent scanning for hours
                norm_root = os.path.normpath(root)
                norm_root_dir = os.path.normpath(root_dir)
                depth = norm_root.count(os.sep) - norm_root_dir.count(os.sep)
                if depth > 6:
                    dirs[:] = [] # Don't go deeper than 6 folders
                    continue
                    
                if filename.lower() in [f.lower() for f in files]:
                    found_path = os.path.join(root, filename)
                    print(f"      [FOUND] {filename} -> {found_path}")
                    return found_path
        return None

    def run_blender_test(self):
        if not self.blender_path:
            print("❌ Blender not found. Please download it from blender.org and install it.")
            return

        print(f"\n✅ Blender Found: {self.blender_path}")
        print("Launching Blender with LEO Bypass (25% Render, Solid Viewport)...")
        
        # Python script to inject into Blender to lower resolution and stop heat
        leo_script = "import bpy; bpy.context.scene.render.resolution_percentage = 25; bpy.context.scene.eevee.taa_render_samples = 16;"
        
        proc = subprocess.Popen([self.blender_path, "--python-expr", leo_script])
        time.sleep(10) # Wait for Blender to load
        
        print("Forcing Viewport to Solid Mode (Zero Heat)...")
        try:
            # Simulate pressing 'Z' and selecting Solid
            pyautogui.hotkey('z')
            time.sleep(1)
            pyautogui.press('down', presses=2)
            pyautogui.press('enter')
        except Exception as e:
            print(f"Auto-GUI failed (might need manual focus): {e}")
            
        print("✅ BLENDER TEST RUNNING: Check the FPS (Bottom Right). It should be 60+.")
        print("Waiting 15 seconds to observe thermal state...")
        time.sleep(15)
        proc.terminate()

    def run_unity_test(self):
        if not self.unity_path:
            print("❌ Unity Editor not found. Skipping.")
            return
            
        print(f"\n✅ Unity Found: {self.unity_path}")
        print("Launching Unity Editor...")
        subprocess.Popen([self.unity_path])
        print("✅ UNITY TEST RUNNING: Editor is launching.")
        time.sleep(15)

    def run_unreal_test(self):
        if not self.unreal_path:
            print("❌ Unreal Editor not found. Skipping.")
            return
            
        print(f"\n✅ Unreal Found: {self.unreal_path}")
        print("Launching Unreal Editor...")
        subprocess.Popen([self.unreal_path])
        print("✅ UNREAL TEST RUNNING: Editor is launching.")
        time.sleep(15)

if __name__ == "__main__":
    leo = LEODeepScanAutopilot()
    print("==================================================")
    print("LEO DEEP SCAN AUTOPILOT TEST PROTOCOL INITIATED")
    print("==================================================")
    
    # Handle non-interactive console runners gracefully
    if not sys.stdin.isatty():
        print("[LEO] Non-interactive environment detected. Skipping test execution.")
    else:
        leo.run_blender_test()
        leo.run_unity_test()
        leo.run_unreal_test()
    
    print("\n🌌 LEO AUTOPILOT TEST COMPLETE.")
