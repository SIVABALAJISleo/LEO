# render_1000_monkeys_output.py
import os
import sys
import shutil
import subprocess
import winreg

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def find_blender():
    alias_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "blender-launcher.exe")
    if os.path.exists(alias_path):
        return alias_path
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\blender.exe")
        path, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if os.path.exists(path):
            return path
    except Exception:
        pass
    try:
        cmd = ["powershell", "-Command", "Get-AppxPackage -Name '*blender*' | Select-Object -ExpandProperty InstallLocation"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        install_dir = res.stdout.strip()
        if install_dir and os.path.exists(install_dir):
            candidate = os.path.join(install_dir, "Blender", "blender.exe")
            if os.path.exists(candidate):
                return candidate
    except Exception:
        pass
    return "blender"

def main():
    blender_bin = find_blender()
    print("==================================================")
    print("📸 RENDERING 1000-MONKEY SCENE FOR VISUAL OUTPUT")
    print("==================================================")
    print(f"Blender binary: {blender_bin}")

    output_img = os.path.abspath("blender_1000_monkeys.png")
    blend_file = os.path.abspath("1000_monkeys_scene.blend")

    render_script = f"""
import bpy
import math

# Clean
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1000 Monkeys
print("Building 1000 monkeys...")
rows = 10
cols = 20
layers = 5

count = 0
for z in range(layers):
    for y in range(rows):
        for x in range(cols):
            if count >= 1000:
                break
            loc = ((x - cols / 2) * 3.5, (y - rows / 2) * 3.5, z * 3.0)
            bpy.ops.mesh.primitive_monkey_add(size=1.5, location=loc)
            obj = bpy.context.active_object
            obj.name = f"LEO_Monkey_{{count}}"
            obj.rotation_euler = (math.radians(20 * (x % 3)), math.radians(20 * (y % 3)), math.radians((count * 15) % 360))
            count += 1

# Lighting
bpy.ops.object.light_add(type='SUN', location=(0, -50, 40))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))

bpy.ops.object.light_add(type='POINT', location=(0, 0, 15))
point = bpy.context.active_object
point.data.energy = 8000

# Camera
bpy.ops.object.camera_add(location=(45, -55, 30))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 5))
target = bpy.context.active_object
constraint = cam.constraints.new(type='TRACK_TO')
constraint.target = target
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# Render settings
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = r"{output_img}"

# Save blend file for interactive viewing
bpy.ops.wm.save_as_mainfile(filepath=r"{blend_file}")
print("Saved blend file to: {blend_file}")

# Render frame
print("Rendering image...")
bpy.ops.render.render(write_still=True)
print("Render complete!")
"""

    # Run Blender background render
    subprocess.run([blender_bin, "-b", "--python-expr", render_script], check=True)
    print(f"✅ Rendered image successfully to: {output_img}")

    # Copy to artifacts directory
    artifact_dir = r"C:\Users\sivab\.gemini\antigravity-ide\brain\a5945a53-e4b3-4f9e-a3d8-f77921de06d3"
    if os.path.exists(artifact_dir):
        dest_img = os.path.join(artifact_dir, "blender_1000_monkeys.png")
        shutil.copy2(output_img, dest_img)
        print(f"✅ Copied to artifact dir: {dest_img}")

    # Open Blender with the saved scene in GUI mode
    print("Launching Blender GUI with 1000 Monkeys scene loaded...")
    subprocess.Popen([blender_bin, blend_file], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    print("✅ Blender GUI window opened!")

if __name__ == "__main__":
    main()
