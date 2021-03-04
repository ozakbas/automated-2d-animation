import bpy


class MouthPanel(bpy.types.Panel):
    bl_idname = "PANEL_PT_mouth"
    bl_label = "Lip-sync"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    def draw(self, context):
        self.layout.operator(
            "mouth.operator", icon='MESH_CUBE', text="Lip sync")


def register():
    bpy.utils.register_class(MouthPanel)


def unregister():
    bpy.utils.unregister_class(MouthPanel)
