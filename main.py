import bpy
import imp
import os
import sys

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import pose

# force a reload
imp.reload(pose)




body = bpy.data.objects["Body"]
head = bpy.data.objects["Head"]
Upper_Arm_L = bpy.data.objects["Upper_Arm_L"]
Upper_Arm_R = bpy.data.objects["Upper_Arm_R"]
Arm_L = bpy.data.objects["Arm_L"]
Arm_R = bpy.data.objects["Arm_R"]


processed_frames = pose.process_json()

pose.drawPose(processed_frames)

# pose.softing
# pose.multiple character check?
# pose conditions: front back, far, close

# blinking

# lip syncing

# background - foreground - props -> conditional on sequences?
