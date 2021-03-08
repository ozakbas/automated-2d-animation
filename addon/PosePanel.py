import bpy


class PosePanel(bpy.types.Panel):
    bl_idname = "PANEL_PT_pose"
    bl_label = "Pose"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        self.layout.operator(
            "open.browser", icon='FILEBROWSER', text="Import JSON folder")
        self.layout.operator(
            "skeleton.operator", icon='BONE_DATA', text="Initialize skeleton")
        self.layout.operator(
            "pose.operator", icon='OUTLINER_OB_ARMATURE', text="Generate poses")


def register():
    bpy.utils.register_class(PosePanel)


def unregister():
    bpy.utils.unregister_class(PosePanel)
