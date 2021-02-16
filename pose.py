import bpy
import os
import math
import json
import constants
from constants import *

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

rotation_threshold = 2
body_threshold = 0.001


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

    for i in range(0, len(processed_frames)):

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
