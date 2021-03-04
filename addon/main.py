import bpy
import json
import os
import math

C = bpy.context
D = bpy.data

UPPER_LEFT = [-4.3202, 2.4302]
BOTTOM_RIGHT = [4.3202, -2.4302]

HEIGHT = BOTTOM_RIGHT[1] - UPPER_LEFT[1]
WIDTH = BOTTOM_RIGHT[0] - UPPER_LEFT[0]

INPUT_WIDTH = 1920
INPUT_HEIGHT = 1080

rotation_threshold = 2
body_threshold = 0.001

body_parts = ["Nose", "Neck", "RShoulder", "RElbow", "RWrist", "LShoulder", "LElbow", "LWrist", "MidHip", "RHip", "RKnee", "RAnkle",
              "LHip", "LKnee", "LAnkle", "REye", "LEye", "REar", "LEar", "LBigToe", "LSmallToe", "LHeel", "RBigToe", "RSmallToe", "RHeel", "Background"]

body = bpy.data.objects["Body"]
head = bpy.data.objects["Head"]
Upper_Arm_L = bpy.data.objects["Upper_Arm_L"]
Upper_Arm_R = bpy.data.objects["Upper_Arm_R"]
Arm_L = bpy.data.objects["Arm_L"]
Arm_R = bpy.data.objects["Arm_R"]

Upper_Leg_L = bpy.data.objects["Upper_Leg_L"]
Upper_Leg_R = bpy.data.objects["Upper_Leg_R"]
Leg_L = bpy.data.objects["Leg_L"]
Leg_R = bpy.data.objects["Leg_R"]
Foot_L = bpy.data.objects["Foot_L"]
Foot_R = bpy.data.objects["Foot_R"]

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


def process_json():

    processed_frames = []

    directory = "C:/Users/ereno/automated-2d-animation/output_json_folder2"
    with os.scandir(directory) as frames:
        for frame in frames:
            with open(frame, 'r') as f:

                data = json.loads(f.read())
                keypoints_raw = data["people"][0]["pose_keypoints_2d"]

                keypoints = []

                # Get x and y values,
                # ignore the detection confidence for now
                for i in range(0, len(keypoints_raw), 3):
                    x = keypoints_raw[i]
                    y = keypoints_raw[i + 1]
                    keypoints.append({"x": x, "y": y})

                processed_frames.append(keypoints)

    return processed_frames


def smoothing_frames(frames):

    new_frames = frames

    # repeat for each keypoint node
    for node in range(0, 24):

        # assign avg of 3 frames unless the distance is more than the threshold
        for i in range(0, len(frames), 3):
            first = frames[i][node]
            second = frames[i+1][node]
            third = frames[i+2][node]

            d1 = calculate_distance(first, second)
            d2 = calculate_distance(second, third)

            threshold = 3

            if((d1 > threshold) or (d2 > threshold)):
                continue

            else:
                avg_x, avg_y = calculate_avg(first, second, third)

                avg_item = {"x": avg_x, "y": avg_y}

                new_frames[i][node] = avg_item
                new_frames[i+1][node] = avg_item
                new_frames[i+2][node] = avg_item

    return new_frames


def calculate_avg(a, b, c):

    x_list = [a["x"], b["x"], c["x"]]
    y_list = [a["y"], b["y"], c["y"]]

    avg_x = sum(x_list) / 3
    avg_y = sum(y_list) / 3

    return avg_x, avg_y


def calculate_distance(a, b):

    x1 = a["x"]
    x2 = b["x"]
    y1 = a["y"]
    y2 = b["y"]

    result = ((((x2 - x1) ** 2) + ((y2-y1) ** 2)) ** 0.5)
    return result


def locate_position(body_part_index, frame):

    input_x = frame[body_part_index]["x"]
    input_y = frame[body_part_index]["y"]

    output_x = UPPER_LEFT[0] + ((input_x / INPUT_WIDTH) * WIDTH)
    output_y = UPPER_LEFT[1] + ((input_y / INPUT_HEIGHT) * HEIGHT)

    return output_x, output_y


def rotate(object, keypoint_index, frame, parent):

    angle = 0

    start_x = frame[keypoint_index]["x"]
    start_y = frame[keypoint_index]["y"]
    end_x = frame[keypoint_index + 1]["x"]
    end_y = frame[keypoint_index + 1]["y"]

    # Find the slope angle
    if (end_x - start_x) != 0:
        angle = math.degrees(math.atan((end_y - start_y) / (end_x - start_x)))

    if(end_x < start_x):
        angle += 180

    rotation_y_value = round(angle - parent - 90, 1)

    # temporary fix for stabil.
    previous_y = object.rotation_euler[1]

    if(abs(previous_y - rotation_y_value) > rotation_threshold):
        object.rotation_euler[1] = math.radians(rotation_y_value)

    return angle


def drawPose(processed_frames):

    upper_Arm_L = 0
    upper_Arm_R = 0
    upper_Leg_L = 0
    upper_Leg_R = 0

    for i in range(0, len(processed_frames), 2):

        for keypoint_index in range(0, 24):

            output_x, output_y = locate_position(
                keypoint_index, processed_frames[i-1])

            object_name = "circle" + str(keypoint_index)

            obj = bpy.data.objects[object_name]
            obj.location = (output_x, 0, output_y)
            obj.keyframe_insert(data_path="location", frame=i)

            if(keypoint_index == 1):

                # temporary fix for stabil.
                previous_x = body.location[0]

                if(abs(previous_x - output_x) > body_threshold):

                    body.location = (output_x, 0, output_y)

                body.keyframe_insert(data_path="location", frame=i)

            # right upper arm
            elif(keypoint_index == 2):
                upper_Arm_R = rotate(Upper_Arm_R, keypoint_index,
                                     processed_frames[i], 0)
                Upper_Arm_R.keyframe_insert(
                    data_path="rotation_euler", frame=i)

            # right arm
            elif(keypoint_index == 3):
                rotate(Arm_R, keypoint_index,
                       processed_frames[i], upper_Arm_R - 90)
                Arm_R.keyframe_insert(data_path="rotation_euler", frame=i)
                upper_Arm_R = 0

            # left upper arm
            elif(keypoint_index == 5):
                upper_Arm_L = rotate(Upper_Arm_L, keypoint_index,
                                     processed_frames[i], 0)
                Upper_Arm_L.keyframe_insert(
                    data_path="rotation_euler", frame=i)

            # left arm
            elif(keypoint_index == 6):
                rotate(Arm_L, keypoint_index,
                       processed_frames[i], upper_Arm_L - 90)
                Arm_L.keyframe_insert(data_path="rotation_euler", frame=i)
                upper_Arm_L = 0

            # right upper leg
            elif(keypoint_index == 9):
                upper_Leg_R = rotate(Upper_Leg_R, keypoint_index,
                                     processed_frames[i], 0)
                Upper_Leg_R.keyframe_insert(
                    data_path="rotation_euler", frame=i)

            # right leg
            elif(keypoint_index == 10):
                rotate(Leg_R, keypoint_index,
                       processed_frames[i], upper_Leg_R - 90)
                Leg_R.keyframe_insert(data_path="rotation_euler", frame=i)
                upper_Leg_R = 0

            # left upper Leg
            elif(keypoint_index == 12):
                upper_Leg_L = rotate(Upper_Leg_L, keypoint_index,
                                     processed_frames[i], 0)
                Upper_Leg_L.keyframe_insert(
                    data_path="rotation_euler", frame=i)

            # left Leg
            elif(keypoint_index == 13):
                rotate(Leg_L, keypoint_index,
                       processed_frames[i], upper_Leg_L - 90)
                Leg_L.keyframe_insert(data_path="rotation_euler", frame=i)
                upper_Leg_L = 0


class PoseClass(bpy.types.Operator):
    bl_idname = 'pose.operator'
    bl_label = 'Add Pose'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        frames = process_json()
        smoothed_frames = smoothing_frames(frames)
        drawPose(smoothed_frames)
        return {"FINISHED"}


class MouthClass(bpy.types.Operator):
    bl_idname = 'mouth.operator'
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
