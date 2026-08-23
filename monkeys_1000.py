# monkeys_1000.py
import bpy
import math

print("[LEO] Wiping scene...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

print("[LEO] Generating 1000 Suzanne monkeys...")
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

print(f"[LEO] Generated {count} monkey objects successfully.")

# Add Sunlight & Point Light
bpy.ops.object.light_add(type='SUN', location=(0, -50, 40))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))

bpy.ops.object.light_add(type='POINT', location=(0, 0, 15))
point = bpy.context.active_object
point.data.energy = 10000

# Add Camera & Target Tracking
bpy.ops.object.camera_add(location=(50, -60, 35))
cam = bpy.context.active_object
bpy.context.scene.camera = cam

bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 5))
target = bpy.context.active_object
constraint = cam.constraints.new(type='TRACK_TO')
constraint.target = target
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# Animate Camera Orbit
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 240
radius = 65
for f in range(1, 241, 10):
    angle = (f / 240.0) * 2 * math.pi
    cam.location.x = radius * math.sin(angle)
    cam.location.y = -radius * math.cos(angle)
    cam.location.z = 25 + 10 * math.sin(angle * 2)
    cam.keyframe_insert(data_path="location", frame=f)

# Configure Viewport & Optimization
scene = bpy.context.scene
scene.render.fps = 60

for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'
                space.shading.color_type = 'OBJECT'
                space.overlay.show_stats = True
                space.region_3d.view_perspective = 'CAMERA'

# Auto play animation
def play_anim():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                try:
                    bpy.ops.screen.animation_play({'window': window, 'screen': window.screen, 'area': area})
                except Exception:
                    pass

bpy.app.timers.register(play_anim, first_interval=0.5)
print("[LEO] Blender 1000 Monkeys Scene Ready & Running!")
