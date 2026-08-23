# render_scene.py
import os
import sys
import shutil
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

blender_bin = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WindowsApps", "blender-launcher.exe")
output_path = os.path.abspath("blender_1000_output.png")
blend_path = os.path.abspath("1000_monkeys.blend")

blender_code = r'''
import bpy
import math

# Clear
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 1000 Monkeys
rows, cols, layers = 10, 20, 5
count = 0
for z in range(layers):
    for y in range(rows):
        for x in range(cols):
            if count >= 1000:
                break
            loc = ((x - cols / 2) * 3.5, (y - rows / 2) * 3.5, z * 3.0)
            bpy.ops.mesh.primitive_monkey_add(size=1.5, location=loc)
            obj = bpy.context.active_object
            obj.rotation_euler = (math.radians(20 * (x % 3)), math.radians(20 * (y % 3)), math.radians((count * 15) % 360))
            count += 1

# Lighting
bpy.ops.object.light_add(type='SUN', location=(0, -50, 40))
sun = bpy.context.active_object
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))

# Camera
bpy.ops.object.camera_add(location=(50, -60, 35))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 5))
target = bpy.context.active_object
constraint = cam.constraints.new(type='TRACK_TO')
constraint.target = target
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# Settings
scene = bpy.context.scene
scene.render.image_settings.file_format = 'PNG'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.filepath = r"''' + output_path + r'''"

# Save blend file
bpy.ops.wm.save_as_mainfile(filepath=r"''' + blend_path + r'''")

# Render
bpy.ops.render.render(write_still=True)
print("SUCCESS_RENDER")
'''

res = subprocess.run([blender_bin, "-b", "--python-expr", blender_code], capture_output=True, text=True)
print("STDOUT:", res.stdout[-800:])
print("STDERR:", res.stderr)

if os.path.exists(output_path):
    print(f"FOUND: {output_path} ({os.path.getsize(output_path)} bytes)")
    artifact_dir = r"C:\Users\sivab\.gemini\antigravity-ide\brain\a5945a53-e4b3-4f9e-a3d8-f77921de06d3"
    dest = os.path.join(artifact_dir, "blender_1000_monkeys.png")
    shutil.copy2(output_path, dest)
    print(f"Copied to artifact dir: {dest}")

# Launch Blender GUI with the generated blend file
subprocess.Popen([blender_bin, blend_path], creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
print("Blender GUI Launched with 1000 Monkeys scene!")
