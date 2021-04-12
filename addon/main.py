import bpy
import json
import os
import math


UPPER_LEFT = [-4.3202, 2.4302]
BOTTOM_RIGHT = [4.3202, -2.4302]

HEIGHT = BOTTOM_RIGHT[1] - UPPER_LEFT[1]
WIDTH = BOTTOM_RIGHT[0] - UPPER_LEFT[0]

INPUT_WIDTH = 1920
INPUT_HEIGHT = 1080

rotation_threshold = 2
body_threshold = 0.001

timestamp = []

gentle_path = ""
pose_path = ""


def replace_mouth():

    m_a = bpy.data.objects["mouth_a"]
    m_f = bpy.data.objects["mouth_f"]
    m_l = bpy.data.objects["mouth_l"]
    m_m = bpy.data.objects["mouth_m"]
    m_t = bpy.data.objects["mouth_t"]
    m_u = bpy.data.objects["mouth_u"]

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


def init_timestamp(gentle_path):

    fps = 30

    if gentle_path != "":
        JSON_file = open(gentle_path)
        data = json.load(JSON_file)
        words = data["words"]

        phones = []

        for word in words:
            if word["case"] == "success":
                frame_index = int(word["start"] * fps)
                for phone in word["phones"]:
                    new_phone = {"start": frame_index, "phone": phone["phone"]}

                    phones.append(new_phone)
                    if round(phone["duration"] * fps) == 0:
                        frame_index += 1
                    else:
                        frame_index += round(phone["duration"] * fps)

        index = 0
        for phone in phones:
            while index <= phone["start"]:
                timestamp.append(phone["phone"])
                index += 1
        print("timestamp initialized: ", timestamp)
    else:
        print("Lip sync JSON is not selected")


def process_json(pose_path):

    if pose_path != "":

        processed_frames = []

        directory = pose_path
        with os.scandir(directory) as frames:
            for frame in frames:
                with open(frame, 'r') as f:

                    # Get the keypoints of the first detected person only
                    data = json.loads(f.read())
                    keypoints_raw = data["people"][0]["pose_keypoints_2d"]

                    keypoints = []

                    # Get x and y values (ignore the detection confidence for now)
                    for i in range(0, len(keypoints_raw), 3):
                        x = keypoints_raw[i]
                        y = keypoints_raw[i + 1]
                        keypoints.append({"x": x, "y": y})

                    processed_frames.append(keypoints)

        return processed_frames
    else:
        print("Pose JSON is not selected")


def smoothing_frames(frames):

    new_frames = frames

    # repeat for each keypoint node
    for node in range(0, 24):

        # assign avg of 3 frames unless the distance is more than the threshold
        for i in range(0, len(frames)-2, 3):
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

    body = bpy.data.objects["Body"]
    Upper_Arm_L = bpy.data.objects["Upper_Arm_L"]
    Upper_Arm_R = bpy.data.objects["Upper_Arm_R"]
    Arm_L = bpy.data.objects["Arm_L"]
    Arm_R = bpy.data.objects["Arm_R"]

    Upper_Leg_L = bpy.data.objects["Upper_Leg_L"]
    Upper_Leg_R = bpy.data.objects["Upper_Leg_R"]
    Leg_L = bpy.data.objects["Leg_L"]
    Leg_R = bpy.data.objects["Leg_R"]

    upper_Arm_L = 0
    upper_Arm_R = 0
    upper_Leg_L = 0
    upper_Leg_R = 0

    for i in range(0, len(processed_frames), 2):

        for keypoint_index in range(0, 24):

            output_x, output_y = locate_position(
                keypoint_index, processed_frames[i-1])

            # Visualisation test with circles
            '''
            object_name = "circle" + str(keypoint_index)
            obj = bpy.data.objects[object_name]
            obj.location = (output_x, 0, output_y)
            obj.keyframe_insert(data_path="location", frame=i)
            '''
            # body
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


def initialize_skeleton():

    body_parts_list = ["Body", "Head", "Upper_Arm_L", "Upper_Arm_R", "Upper_Leg_L", "Upper_Leg_R", "Arm_L",
                       "Arm_R", "Leg_L", "Leg_R", "Eyes", "mouth_a", "mouth_f", "mouth_l", "mouth_m", "mouth_t", "mouth_u"]

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


class SkeletonClass(bpy.types.Operator):
    bl_idname = 'skeleton.operator'
    bl_label = 'Add Skeleton'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        initialize_skeleton()
        return {"FINISHED"}


class PoseClass(bpy.types.Operator):
    bl_idname = 'pose.operator'
    bl_label = 'Add Pose'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        frames = process_json(pose_path)
        smoothed_frames = smoothing_frames(frames)
        drawPose(smoothed_frames)
        return {"FINISHED"}


class MouthClass(bpy.types.Operator):
    bl_idname = 'mouth.operator'
    bl_label = 'Add Mouth'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        init_timestamp(gentle_path)
        replace_mouth()
        return {"FINISHED"}


class OpenBrowser(bpy.types.Operator):
    bl_idname = "open.browser"
    bl_label = "Open browser & get filepath"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")
    # somewhere to remember the address of the file

    def execute(self, context):
        filepath = self.filepath
        global pose_path
        pose_path = filepath

        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class OpenBrowser2(bpy.types.Operator):
    bl_idname = "open.browser2"
    bl_label = "Open browser & get filepath"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        filepath = self.filepath
        global gentle_path
        gentle_path = filepath
        # Window>>>Toggle systen console

        return {'FINISHED'}

    def invoke(self, context, event):

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(SkeletonClass)
    bpy.utils.register_class(PoseClass)
    bpy.utils.register_class(MouthClass)
    bpy.utils.register_class(OpenBrowser)
    bpy.utils.register_class(OpenBrowser2)


def unregister():
    bpy.utils.unregister_class(SkeletonClass)
    bpy.utils.unregister_class(PoseClass)
    bpy.utils.unregister_class(MouthClass)
    bpy.utils.unregister_class(OpenBrowser)
    bpy.utils.unregister_class(OpenBrowser2)
