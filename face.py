import bpy
import json

phoneDict = ['aa_B', 'aa_I', 'ae_B', 'ae_I', 'ah_B', 'ah_E', 'ah_I', 'ah_S', 'ao_B', 'ao_I', 'aw_I', 'ay_E', 'ay_I',
             'b_B', 'b_E', 'b_I', 'ch_B', 'ch_E', 'd_B', 'd_E', 'd_I', 'dh_B', 'dh_I', 'eh_B', 'eh_I', 'er_B',
             'er_E', 'er_I', 'er_S', 'ey_B', 'ey_I', 'ey_S', 'f_B', 'f_E', 'f_I', 'g_B', 'g_I', 'hh_B', 'ih_B',
             'ih_I', 'iy_B', 'iy_E', 'iy_I', 'jh_B', 'jh_E', 'jh_I', 'k_B', 'k_E', 'k_I', 'l_B', 'l_E', 'l_I',
             'm_B', 'm_E', 'm_I', 'n_B', 'n_E', 'n_I', 'ng_E', 'ng_I', 'oov_S', 'ow_B', 'ow_E', 'ow_I', 'oy_I',
             'p_B', 'p_E', 'p_I', 'r_B', 'r_E', 'r_I', 's_B', 's_E', 's_I', 'sh_E', 'sh_I', 't_B', 't_E', 't_I',
             'th_B', 'th_E', 'th_I', 'uh_I', 'uw_E', 'uw_I', 'v_B', 'v_E', 'v_I', 'w_B', 'w_I', 'y_B', 'y_I', 'z_B',
             'z_E', 'z_I', 'zh_I']

m_a = bpy.data.objects["mouth_a"]
m_f = bpy.data.objects["mouth_f"]
m_l = bpy.data.objects["mouth_l"]
m_m = bpy.data.objects["mouth_m"]
m_t = bpy.data.objects["mouth_t"]
m_u = bpy.data.objects["mouth_u"]

mouth_list = [m_a, m_f, m_l, m_m, m_t, m_u]


def replace_mouth(self):

    frame = int(self.frame_current)
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

    # Hide mouths both in render and view mode
    for i in mouth_list:
        i.hide_render = i.hide_viewport = True
        i.keyframe_insert(data_path="location", frame=frame)

    selected_mouth.hide_render = selected_mouth.hide_viewport = False

    print(frame)


timestamp = []


def init_timestamp():

    JSON_file = open("C:/Users/ereno/automated-2d-animation/gentle.json")
    data = json.load(JSON_file)
    words = data["words"]

    total_seconds = words[len(words) - 1]["end"]

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

    print(timestamp)


'''
expression_input = [
    {frame: 0, eyes: "confused", pupil: "RB", mouth: "positive"},
    {frame: 70, eyes: "angry", pupil: "RB", mouth: "negative"},
    {frame: 290, eyes: "happy", pupil: "RB", mouth: "positive"},
    {frame: 350, eyes: "neutral", pupil: "RB", mouth: "positive"},

]

jest_input = []

blink_input = 3

eyelids_layer = bpy.data.grease_pencils['GPencil.012'].layers["eyelids"]

frame = eyelids_layer.frames[0]

eyes.mode_set(mode=‘EDIT’)


INPUT:

1. blinks period -> every 3 seconds 

2. triggers
        
    0 sad, pupil C
    24 confused, pupil LB LU RB RU L R U D
    27 neutral , pupil R

3. eye size

phases:

draw eyebrow (sad)
draw pupil (LB)
draw mouth (sad + jest input)
draw blinks


'''
