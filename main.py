import bpy
import json

C = bpy.context
D = bpy.data

'''

phoneDict = ['aa_B', 'aa_I', 'ae_B', 'ae_I', 'ah_B', 'ah_E', 'ah_I', 'ah_S', 'ao_B', 'ao_I', 'aw_I', 'ay_E', 'ay_I',
             'b_B', 'b_E', 'b_I', 'ch_B', 'ch_E', 'd_B', 'd_E', 'd_I', 'dh_B', 'dh_I', 'eh_B', 'eh_I', 'er_B',
             'er_E', 'er_I', 'er_S', 'ey_B', 'ey_I', 'ey_S', 'f_B', 'f_E', 'f_I', 'g_B', 'g_I', 'hh_B', 'ih_B',
             'ih_I', 'iy_B', 'iy_E', 'iy_I', 'jh_B', 'jh_E', 'jh_I', 'k_B', 'k_E', 'k_I', 'l_B', 'l_E', 'l_I',
             'm_B', 'm_E', 'm_I', 'n_B', 'n_E', 'n_I', 'ng_E', 'ng_I', 'oov_S', 'ow_B', 'ow_E', 'ow_I', 'oy_I',
             'p_B', 'p_E', 'p_I', 'r_B', 'r_E', 'r_I', 's_B', 's_E', 's_I', 'sh_E', 'sh_I', 't_B', 't_E', 't_I',
             'th_B', 'th_E', 'th_I', 'uh_I', 'uw_E', 'uw_I', 'v_B', 'v_E', 'v_I', 'w_B', 'w_I', 'y_B', 'y_I', 'z_B',
             'z_E', 'z_I', 'zh_I']
'''

timestamp = []


def replace_mouth():

    m_a = D.objects["mouth_a"]
    m_f = D.objects["mouth_f"]
    m_l = D.objects["mouth_l"]
    m_m = D.objects["mouth_m"]
    m_t = D.objects["mouth_t"]
    m_u = D.objects["mouth_u"]

    mouth_list = [m_a, m_f, m_l, m_m, m_t, m_u]

    for frame in range(len(timestamp)):

        # first letter of the phone
        ts = timestamp[frame][0]

        if ts == "a" or ts == "e" or ts == "h":
            selected_mouth = m_a
        elif ts == "y" or ts == "l":
            selected_mouth = m_l
        elif ts == "u" or ts == "o" or ts == "r":
            selected_mouth = m_u
        elif ts == "m" or ts == "b" or ts == "p":
            selected_mouth = m_m
        elif ts == "f" or ts == "v" or ts == "w":
            selected_mouth = m_f
        else:
            selected_mouth = m_t

        # Reset mouths both in render and view mode
        for i in mouth_list:
            i.hide_render = i.hide_viewport = True
            i.keyframe_insert(data_path="hide_render", frame=frame)
            i.keyframe_insert(data_path="hide_viewport", frame=frame)

        selected_mouth.hide_render = selected_mouth.hide_viewport = False
        selected_mouth.keyframe_insert(data_path="hide_render", frame=frame)
        selected_mouth.keyframe_insert(data_path="hide_viewport", frame=frame)


def init_timestamp():
    JSON_file = open("C:/Users/ereno/automated-2d-animation/gentle.json")
    data = json.load(JSON_file)
    words = data["words"]

    phones = []

    for word in words:
        frame_index = int(word["start"] * 24)
        for phone in word["phones"]:
            new_phone = {"start": frame_index, "phone": phone["phone"]}

            phones.append(new_phone)
            if round(phone["duration"] * 24) == 0:
                frame_index += 1
            else:
                frame_index += round(phone["duration"] * 24)

    index = 0
    for phone in phones:
        while index <= phone["start"]:
            timestamp.append(phone["phone"])
            index += 1
    print("timestamp initialized: ", timestamp)


class PoseClass(bpy.types.Operator):
    bl_idname = 'pose_id'
    bl_label = 'Add Pose'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return {"FINISHED"}


class MouthClass(bpy.types.Operator):
    bl_idname = 'mouth_id'
    bl_label = 'Add Mouth'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        init_timestamp()
        replace_mouth()
        return {"FINISHED"}


def register():
    bpy.utils.register_class(PoseClass)
    bpy.utils.register_class(MouthClass)


def unregister():
    bpy.utils.unregister_class(PoseClass)
    bpy.utils.unregister_class(MouthClass)
