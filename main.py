
import bpy
import imp
import os
import sys

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import pose
import face

# force a reload
imp.reload(pose)
imp.reload(face)


frames = pose.process_json()
smoothed_frames = pose.smoothing_frames(frames)


#pose.drawPose(smoothed_frames)

face.init_timestamp()

#bpy.app.handlers.frame_change_pre.clear()       
bpy.app.handlers.frame_change_pre.append(face.replace_mouth)

