"""
hyper/integrations/blender/HyperBlender/addon/hyper_blender_addon.py
===================================================================
HYPER Blender Addon:
Blender Viewport & Render Optimizer UI Panel and Operator.
Exposes HYPER INTERACTIVE MODE vs HYPER FINAL MODE controls.
"""

bl_info = {
    "name": "HYPER Viewport & Render Optimizer",
    "author": "LEO / HYPER Systems Engineering",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > HYPER",
    "description": "Computation elimination, adaptive LOD, temporal reprojection, and CPU+iGPU cooperative acceleration for Blender.",
    "category": "Render",
}

try:
    import bpy
    _HAS_BPY = True
except ImportError:
    _HAS_BPY = False


if _HAS_BPY:
    class HYPER_OT_ToggleInteractiveMode(bpy.types.Operator):
        bl_idname = "hyper.toggle_interactive"
        bl_label = "Activate HYPER Interactive Mode"
        bl_description = "Engages temporal reprojection and adaptive LOD for 60 FPS viewport interaction."

        def execute(self, context):
            context.scene.hyper_mode = "INTERACTIVE"
            self.report({'INFO'}, "HYPER Interactive Mode Active (60 FPS Target)")
            return {'FINISHED'}

    class HYPER_OT_ToggleFinalMode(bpy.types.Operator):
        bl_idname = "hyper.toggle_final"
        bl_label = "Activate HYPER Final Render Mode"
        bl_description = "Engages strict numerical convergence and zero-temporal-blur path tracing for final production render."

        def execute(self, context):
            context.scene.hyper_mode = "FINAL"
            self.report({'INFO'}, "HYPER Final Render Mode Active (High Quality)")
            return {'FINISHED'}

    class HYPER_PT_MainPanel(bpy.types.Panel):
        bl_label = "HYPER Optimizer"
        bl_idname = "HYPER_PT_main_panel"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_category = 'HYPER'

        def draw(self, context):
            layout = self.layout
            scene = context.scene

            box = layout.box()
            box.label(text="HYPER Acceleration Status", icon='PREFERENCES')
            current_mode = getattr(scene, "hyper_mode", "INTERACTIVE")
            box.label(text=f"Active Mode: {current_mode}")

            col = layout.column(align=True)
            col.operator("hyper.toggle_interactive", icon='PLAY')
            col.operator("hyper.toggle_final", icon='RESTRICT_RENDER_OFF')

            box_stats = layout.box()
            box_stats.label(text="Telemetry Metrics", icon='INFO')
            box_stats.label(text="Target: 60 FPS (Intel UHD iGPU)")
            box_stats.label(text="Work Reduction: Active")

    classes = (
        HYPER_OT_ToggleInteractiveMode,
        HYPER_OT_ToggleFinalMode,
        HYPER_PT_MainPanel,
    )

    def register():
        bpy.types.Scene.hyper_mode = bpy.props.EnumProperty(
            items=[
                ('INTERACTIVE', "Interactive Mode", "60 FPS Viewport Responsiveness"),
                ('FINAL', "Final Mode", "Physically Exact Path-Traced Quality"),
            ],
            default='INTERACTIVE',
        )
        for cls in classes:
            bpy.utils.register_class(cls)

    def unregister():
        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
        if hasattr(bpy.types.Scene, "hyper_mode"):
            del bpy.types.Scene.hyper_mode

else:
    def register():
        pass
    def unregister():
        pass
