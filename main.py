
import pose
import bpy
import imp
import os
import sys

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)


# force a reload
imp.reload(pose)

# TODO parenting & masking

frames = pose.process_json()

smoothed_frames = pose.smoothing_frames(frames)

pose.drawPose(smoothed_frames)


# pose.multiple character check?
# pose conditions: front back, far, close

# blinking

# lip syncing

# background - foreground - props -> conditional on sequences?
