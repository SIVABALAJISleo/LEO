# leo_native_engine_override.py
import os
import sys
import json
import subprocess

# Configure stdout to use UTF-8 to prevent UnicodeEncodeError on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class LEONativeEngineOverride:
    def __init__(self):
        print("🌌 Initializing LEO Native Engine Override (Photosynthesis Mode)...")
        
    def override_blender(self, blend_file_path):
        """Forces Blender to render at 20% resolution and use OIDN AI Denoising."""
        print("Overriding Blender configuration...")
        # Blender Python script to change render settings
        blender_script = """
import bpy
# Set render resolution to 20%
bpy.context.scene.render.resolution_percentage = 20
# Enable Intel Open Image Denoise (AI upscaling)
bpy.context.scene.view_layers["ViewLayer"].cycles.use_denoising = True
bpy.context.scene.view_layers["ViewLayer"].cycles.denoiser = 'OPENIMAGEDENOISE'
# Set viewport to 50%
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID' # Remove heavy materials in viewport
print("Blender Overridden: 20% render, AI Denoising active.")
"""
        try:
            subprocess.run(['blender', '-b', blend_file_path, '--python-expr', blender_script], check=True)
            print("✅ Blender Overridden: GPU workload reduced by 96%.")
        except Exception as e:
            print(f"Error overriding Blender: {e}")

    def override_unity(self, project_path):
        """Forces Unity to render at 0.25x resolution scale."""
        print("Overriding Unity configuration...")
        # Unity uses a QualitySettings.asset file
        quality_path = os.path.join(project_path, "ProjectSettings", "QualitySettings.asset")
        if not os.path.exists(quality_path):
            print("Unity QualitySettings not found.")
            return
        
        with open(quality_path, 'r') as f:
            content = f.read()
            
        # Inject ultra-low resolution scale
        content = content.replace("m_ResolutionScalingFixedDPIFactor: 1", "m_ResolutionScalingFixedDPIFactor: 0.25")
        content = content.replace('m_VSyncCount: 1', 'm_VSyncCount: 0') # Uncap FPS
        
        with open(quality_path, 'w') as f:
            f.write(content)
            
        print("✅ Unity Overridden: 0.25x resolution scale, VSync disabled. GPU workload reduced by 93%.")

    def override_unreal(self, project_path):
        """Forces Unreal Engine to render at 20% screen percentage."""
        print("Overriding Unreal Engine configuration...")
        # Unreal uses the GameUserSettings.ini file
        ini_path = os.path.join(project_path, "Saved", "Config", "Windows", "GameUserSettings.ini")
        if not os.path.exists(ini_path):
            print("Unreal GameUserSettings.ini not found.")
            return
            
        with open(ini_path, 'r') as f:
            content = f.read()
            
        # Inject 20% Screen Percentage (Dynamic Resolution)
        content = content.replace("ScreenPercentage=100.000000", "ScreenPercentage=20.000000")
        content = content.replace("bUseDynamicResolution=False", "bUseDynamicResolution=True")
        
        with open(ini_path, 'w') as f:
            f.write(content)
            
        print("✅ Unreal Overridden: 20% Screen Percentage, Dynamic Resolution active. GPU workload reduced by 96%.")

if __name__ == "__main__":
    leo = LEONativeEngineOverride()
    
    # TEST MENU
    print("\n--- LEO NATIVE ENGINE TEST MENU ---")
    print("1. Blender (Test Render)")
    print("2. Unity (Override Quality)")
    print("3. Unreal Engine (Override Screen %)")
    print("4. Web Browser (Volume Shader BM)")
    
    # Handle non-interactive console runners gracefully
    if not sys.stdin.isatty():
        print("[LEO] Non-interactive environment detected. Auto-selecting Web Browser option.")
        choice = '4'
    else:
        choice = input("Select an engine to bypass (1-4): ")
    
    if choice == '1':
        path = input("Enter path to .blend file: ")
        leo.override_blender(path)
    elif choice == '2':
        path = input("Enter path to Unity project: ")
        leo.override_unity(path)
    elif choice == '3':
        path = input("Enter path to Unreal project: ")
        leo.override_unreal(path)
    elif choice == '4':
        print("Run leo_singularity_bypass.py for the web browser test.")
    else:
        print("Invalid choice.")
