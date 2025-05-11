bl_info = {
    "name": "Scale by Ratio",
    "author": "Rafa G.M.",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Scale by Ratio",
    "description": "Scale selected objects based on a ratio like 1:700 or 45:1 with optional apply transform",
    "category": "Object",
}

import bpy
from mathutils import Vector

class OBJECT_PT_scale_by_ratio_panel(bpy.types.Panel):
    bl_label = "Scale by Ratio"
    bl_idname = "OBJECT_PT_scale_by_ratio_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Scale by Ratio'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        selected_objects = context.selected_objects
        lhs = scene.scale_ratio_lhs
        rhs = scene.scale_ratio_rhs

        layout.prop(scene, "scale_ratio_lhs")
        layout.prop(scene, "scale_ratio_rhs")
        layout.prop(scene, "scale_apply_transform")

        # Show selection stats
        box = layout.box()
        box.label(text=f"Selected objects: {len(selected_objects)}")

        if selected_objects:
            from mathutils import Vector

            # Bounding box calculation
            min_coord = [float('inf')] * 3
            max_coord = [float('-inf')] * 3

            for obj in selected_objects:
                world_bounds = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
                for i in range(3):
                    coords = [v[i] for v in world_bounds]
                    min_coord[i] = min(min_coord[i], min(coords))
                    max_coord[i] = max(max_coord[i], max(coords))

            size = [max_coord[i] - min_coord[i] for i in range(3)]
            scale_factor = lhs / rhs if rhs != 0 else 0
            new_size = [s * scale_factor for s in size]

            # Unit settings
            unit_settings = context.scene.unit_settings
            unit_scale = unit_settings.scale_length
            unit_name = unit_settings.length_unit
            if unit_name == 'NONE':
                unit_name = "BU"  # Blender Units fallback

            axis_labels = ['X', 'Y', 'Z']

            col = box.column()
            col.label(text="Current bounds:")
            for i in range(3):
                val = size[i] * unit_scale
                col.label(text=f"  {axis_labels[i]}: {val:.4f} {unit_name}")

            col.label(text="Expected bounds:")
            for i in range(3):
                val = new_size[i] * unit_scale
                col.label(text=f"  {axis_labels[i]}: {val:.4f} {unit_name}")

        else:
            box.label(text="Current bounds: N/A")
            box.label(text="Expected bounds: N/A")

        layout.operator("object.scale_by_ratio")

class OBJECT_OT_scale_by_ratio(bpy.types.Operator):
    bl_label = "Apply Ratio Scale"
    bl_idname = "object.scale_by_ratio"
    bl_description = "Scale selected objects based on the given ratio"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        lhs = context.scene.scale_ratio_lhs
        rhs = context.scene.scale_ratio_rhs
        apply_transform = context.scene.scale_apply_transform

        selected_objects = context.selected_objects

        if not selected_objects:
            self.show_popup("No objects selected to scale.")
            return {'CANCELLED'}

        if rhs == 0:
            self.report({'ERROR'}, "Right side of ratio cannot be zero.")
            return {'CANCELLED'}

        scale_factor = lhs / rhs

        for obj in selected_objects:
            obj.scale = [s * scale_factor for s in obj.scale]

        if apply_transform:
            bpy.ops.object.select_all(action='DESELECT')
            for obj in selected_objects:
                obj.select_set(True)
                context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        self.report({'INFO'}, f"Scaled {len(selected_objects)} object(s) by {scale_factor:.4f}" +
                               (" and applied transforms." if apply_transform else "."))
        return {'FINISHED'}

    def show_popup(self, message):
        def draw(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(draw, title="Warning", icon='ERROR')




def register():
    bpy.utils.register_class(OBJECT_PT_scale_by_ratio_panel)
    bpy.utils.register_class(OBJECT_OT_scale_by_ratio)
    bpy.types.Scene.scale_ratio_lhs = bpy.props.FloatProperty(
        name="From (Left Side)", default=1.0, min=0.0001)
    bpy.types.Scene.scale_ratio_rhs = bpy.props.FloatProperty(
        name="To (Right Side)", default=700.0, min=0.0001)
    bpy.types.Scene.scale_apply_transform = bpy.props.BoolProperty(
        name="Apply Transform", default=True)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_scale_by_ratio_panel)
    bpy.utils.unregister_class(OBJECT_OT_scale_by_ratio)
    del bpy.types.Scene.scale_ratio_lhs
    del bpy.types.Scene.scale_ratio_rhs
    del bpy.types.Scene.scale_apply_transform

if __name__ == "__main__":
    register()
