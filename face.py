
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

'''
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
