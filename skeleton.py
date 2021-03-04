import bpy


body_parts_list = ["Body", "Head", "Upper_Arm_L", "Upper_Arm_R", "Upper_Leg_L", "Upper_Leg_R", "Arm_L",
                   "Arm_R", "Leg_L", "Leg_R", "Eyes", "mouth_a", "mouth_f", "mouth_l", "mouth_m", "mouth_t", "mouth_u"]


def create_gpencils():

    collection = bpy.data.collections.new("Character")
    collection2 = bpy.data.collections.new("Mouths")
    bpy.context.scene.collection.children.link(collection)
    bpy.context.scene.collection.children.link(collection2)

    for i in range(len(body_parts_list)):

        obj_name = body_parts_list[i]

        bpy.ops.object.gpencil_add(location=(0, 0, 0), type='EMPTY')
        bpy.context.scene.objects["GPencil"].name = obj_name

        obj = bpy.data.objects[obj_name]

        if i < 11:
            collection.objects.link(obj)
        else:
            collection2.objects.link(obj)


create_gpencils()
