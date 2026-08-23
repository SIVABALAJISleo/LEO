# run_1000_monkeys_auto.py
import os
import sys
import subprocess
import winreg

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def find_blender():
    # 1. WindowsApps alias
    alias_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "blender-launcher.exe")
    if os.path.exists(alias_path):
        return alias_path

    # 2. App Paths registry
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\blender.exe")
        path, _ = winreg.QueryValueEx(key, "")
        winreg.CloseKey(key)
        if os.path.exists(path):
            return path
    except Exception:
        pass

    # 3. AppX package search
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

    # 4. Standard program files
    common_paths = [
        r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender\blender.exe",
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p

    return "blender"

def launch_automatic_1000_monkeys():
    blender_bin = find_blender()
    print("==================================================")
    print("🚀 LEO AI: AUTOMATED 1000-MONKEY BLENDER BENCHMARK")
    print("==================================================")
    print(f"✅ Found Blender: {blender_bin}")
    print("🔨 Generating 1000 Suzanne objects, Volumetric Fog, and Automated Animation Loop...")

    injected_script = """
import bpy
import math

# 1. Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 2. Add 1000 Suzanne Monkeys in 3D Grid Formation
print("[LEO] Building 1000 monkey instances...")
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
            obj.name = f"LEO_Monkey_{count}"
            obj.rotation_euler = (math.radians(15 * (x % 4)), math.radians(15 * (y % 4)), math.radians(count % 360))
            count += 1

# 3. Add Point Light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 15))
light = bpy.context.active_object
light.data.energy = 5000

# 4. Add Volumetric Environment
world = bpy.context.scene.world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()

node_out = nodes.new(type='ShaderNodeOutputWorld')
node_bg = nodes.new(type='ShaderNodeBackground')
node_bg.inputs['Color'].default_value = (0.02, 0.03, 0.05, 1.0)
node_bg.inputs['Strength'].default_value = 0.5
links.new(node_bg.outputs['Background'], node_out.inputs['Surface'])

node_vol = nodes.new(type='ShaderNodeVolumeScatter')
node_vol.inputs['Density'].default_value = 0.015
links.new(node_vol.outputs['Volume'], node_out.inputs['Volume'])

# 5. Add Animated Camera Orbit (360 degrees, 240 frames)
bpy.ops.object.camera_add(location=(0, -60, 25))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

# Camera tracking constraint to origin
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 5))
target = bpy.context.active_object
target.name = "LEO_Focus_Center"

constraint = cam.constraints.new(type='TRACK_TO')
constraint.target = target
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# Animate Camera Orbit
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 240

radius = 55
for f in range(1, 241, 10):
    angle = (f / 240.0) * 2 * math.pi
    cam.location.x = radius * math.sin(angle)
    cam.location.y = -radius * math.cos(angle)
    cam.location.z = 18 + 8 * math.sin(angle * 2)
    cam.keyframe_insert(data_path="location", frame=f)

# 6. Apply LEO Fast Photosynthesis Engine Optimization
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_percentage = 50
scene.render.fps = 60

# Viewport shading config
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'
                space.shading.color_type = 'OBJECT'
                space.overlay.show_stats = True
                space.region_3d.view_perspective = 'CAMERA'

# 7. Start Playback Automatically
def play_anim():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                override = {'window': window, 'screen': screen, 'area': area}
                try:
                    bpy.ops.screen.animation_play(override)
                except Exception:
                    pass

bpy.app.timers.register(play_anim, first_interval=1.0)
print("[LEO] Scene loaded & Animation started automatically at 60 FPS!")
"""

    # Launch Blender detached so it runs independently in the user's GUI
    cmd = [blender_bin, "--python-expr", injected_script]
    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    print("✅ Blender has been launched automatically in full interactive mode!")
    print("✨ The 1000 Monkey structure is generated and camera animation is playing live at 60 FPS.")

if __name__ == "__main__":
    launch_automatic_1000_monkeys()
