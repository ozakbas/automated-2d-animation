import bpy


class PosePanel(bpy.types.Panel):
    bl_idname = "PANEL_PT_pose"
    bl_label = "Pose"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        self.layout.operator(
            "skeleton.operator", icon='MESH_CUBE', text="Initialize skeleton")
        self.layout.operator(
            "pose.operator", icon='MESH_CUBE', text="Generate poses")


def register():
    bpy.utils.register_class(PosePanel)


def unregister():
    bpy.utils.unregister_class(PosePanel)
