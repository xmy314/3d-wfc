# structural
# solid, air, slope, roof, pillars, arc

# default sprite orientation for future reference
#     y+1
# x-1     z-1
#      o 
# z+1     x+1
#     y-1

# snakeviz /tmp/tmp.prof

import os
from datetime import datetime
import numpy as np
import cv2
from wfc_solver import solveWFC,extendConstraints

# render functions
def combine(bg,fg,fg_off):
    abg = bg[fg_off[0]:fg_off[0]+fg.shape[0],fg_off[1]:fg_off[1]+fg.shape[1],3] / 255.0
    afg = fg[:,:,3] / 255.0

    # set adjusted colors
    for color in range(0, 3):
        bg[fg_off[0]:fg_off[0]+fg.shape[0],fg_off[1]:fg_off[1]+fg.shape[1],color] = afg * fg[:,:,color] + \
            abg * bg[fg_off[0]:fg_off[0]+fg.shape[0],fg_off[1]:fg_off[1]+fg.shape[1],color] * (1 - afg)

    # set adjusted alpha and denormalize back to 0-255
    bg[fg_off[0]:fg_off[0]+fg.shape[0],fg_off[1]:fg_off[1]+fg.shape[1],3] = (1 - (1 - abg) * (1 - afg)) * 255

def drawArena(arena,sprite_sheet,sprite_id,sprite_sheet_column_count,sprite_sheet_square_size,path="output",name=""):
    if name=="":
        time=datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        name = f"{time}.png"
    
    max_d=0
    for position in arena:
        max_d=max(max_d,max([abs(x) for x in position]))

    world_to_camera=np.array(
        [
            [6,-12,6,(sprite_sheet_square_size*max_d+sprite_sheet_square_size)//2],
            [12,0,-12,(sprite_sheet_square_size*max_d+sprite_sheet_square_size)//2],
        ]
    )

    canvas = np.zeros((sprite_sheet_square_size*(max_d+2),sprite_sheet_square_size*(max_d+2),4))

    all_positions=list(arena.keys())
    all_positions.sort(key=lambda x: sum(x))

    for position in all_positions:

        # not settleed skip
        if len(arena[position])!=1:continue
        
        for structure in arena[position]:break

        # else, draw it
        this_sprite_id=sprite_id[structure]
        sprite=sprite_sheet[
            (this_sprite_id//sprite_sheet_column_count)*sprite_sheet_square_size:
            (this_sprite_id//sprite_sheet_column_count+1)*sprite_sheet_square_size,
            (this_sprite_id%sprite_sheet_column_count)*sprite_sheet_square_size:
            (this_sprite_id%sprite_sheet_column_count+1)*sprite_sheet_square_size]
        combine(canvas,sprite,np.matmul(world_to_camera,[*position,1]))

    cv2.imwrite( os.path.join(path,name),canvas)

STRU={
    "AIR___":0,
    "SOLID_":1,
    "POLE__":2,
    "ROOF__":3,
    "ARC__X":4,
    "ARC__Z":5,
    "SLOPE0":6,
    "SLOPE1":7,
    "SLOPE2":8,
    "SLOPE3":9,
}

# input constraints, if anything is inconsistent, it would halt during extending the constraints.
raw_constraints={
    STRU["AIR___"]:{},
    STRU["SOLID_"]:{
        ( 0,-1, 0):{STRU["SOLID_"],STRU["POLE__"],STRU["ARC__X"],STRU["ARC__Z"]}},
    STRU["POLE__"]:{
        ( 0,-1, 0):{STRU["SOLID_"],STRU["POLE__"]},
        ( 0, 1, 0):{STRU["SOLID_"],STRU["POLE__"]}},
    STRU["ROOF__"]:{
        ( 0,-1, 0):{STRU["SOLID_"]},
        ( 0, 1, 0):{STRU["AIR___"]},
        ( 1, 1, 0):{STRU["AIR___"]},
        ( 0, 1, 1):{STRU["AIR___"]},
        (-1, 1, 0):{STRU["AIR___"]},
        ( 0, 1,-1):{STRU["AIR___"]},},
    STRU["ARC__X"]:{
        ( 0, 1, 0):{STRU["SOLID_"],STRU["POLE__"],STRU["ROOF__"],STRU["SLOPE0"],STRU["SLOPE1"],STRU["SLOPE2"],STRU["SLOPE3"]},
        ( 1, 0, 0):{STRU["SOLID_"],STRU["ARC__X"]},
        (-1, 0, 0):{STRU["SOLID_"],STRU["ARC__X"]},},
    STRU["ARC__Z"]:{
        ( 0, 1, 0):{STRU["SOLID_"],STRU["POLE__"],STRU["ROOF__"],STRU["SLOPE0"],STRU["SLOPE1"],STRU["SLOPE2"],STRU["SLOPE3"]},
        ( 0, 0, 1):{STRU["SOLID_"],STRU["ARC__Z"]},
        ( 0, 0,-1):{STRU["SOLID_"],STRU["ARC__Z"]}},
    STRU["SLOPE0"]:{
        ( 0,-1, 0):{STRU["SOLID_"],STRU["POLE__"],STRU["ARC__X"]},
        ( 0, 1, 0):{STRU["AIR___"],STRU["ARC__X"],STRU["ARC__Z"]},
        (-1, 0, 0):{STRU["SOLID_"]},
        ( 1, 0, 0):{STRU["AIR___"],STRU["POLE__"]},
        (-1, 1, 0):{STRU["AIR___"],STRU["POLE__"],STRU["SLOPE0"]},
        ( 1,-1, 0):{STRU["SOLID_"],STRU["SLOPE0"]},},
    STRU["SLOPE1"]:{
        ( 0,-1, 0):{STRU["SOLID_"],STRU["POLE__"],STRU["ARC__Z"]},
        ( 0, 1, 0):{STRU["AIR___"],STRU["ARC__X"],STRU["ARC__Z"]},
        ( 0, 0,-1):{STRU["SOLID_"]},
        ( 0, 0, 1):{STRU["AIR___"],STRU["POLE__"]},
        ( 0, 1,-1):{STRU["AIR___"],STRU["POLE__"],STRU["SLOPE1"]},
        ( 0,-1, 1):{STRU["SOLID_"],STRU["SLOPE1"]},},
    STRU["SLOPE2"]:{
        ( 0,-1, 0):{STRU["SOLID_"],STRU["POLE__"],STRU["ARC__X"]},
        ( 0, 1, 0):{STRU["AIR___"],STRU["ARC__X"],STRU["ARC__Z"]},
        ( 1, 0, 0):{STRU["SOLID_"]},
        (-1, 0, 0):{STRU["AIR___"],STRU["POLE__"]},
        ( 1, 1, 0):{STRU["AIR___"],STRU["POLE__"],STRU["SLOPE2"]},
        (-1,-1, 0):{STRU["SOLID_"],STRU["SLOPE2"]},},
    STRU["SLOPE3"]:{
        ( 0,-1, 0):{STRU["SOLID_"],STRU["POLE__"],STRU["ARC__Z"]},
        ( 0, 1, 0):{STRU["AIR___"],STRU["ARC__X"],STRU["ARC__Z"]},
        ( 0, 0, 1):{STRU["SOLID_"]},
        ( 0, 0,-1):{STRU["AIR___"],STRU["POLE__"]},
        ( 0, 1, 1):{STRU["AIR___"],STRU["POLE__"],STRU["SLOPE3"]},
        ( 0,-1,-1):{STRU["SOLID_"],STRU["SLOPE3"]},},
}

# import pickle

# extended=extendConstraints(raw_constraints,set(raw_constraints.keys()),(0,0,0))

# # with open('saved_dictionary.pkl', 'wb') as f:
# #     pickle.dump(extended, f)

# with open('saved_dictionary.pkl', 'rb') as f:
#     reference_dict = pickle.load(f)

# assert reference_dict==extended

arena=solveWFC(raw_constraints)

sprite_sheet=cv2.imread("template3.png",cv2.IMREAD_UNCHANGED)

sprite_id={
    0:15,
    1:0,
    2:1,
    3:2,
    4:3,
    5:4,
    6:5,
    7:6,
    8:7,
    9:8,
}

sprite_sheet_column_count=4

sprite_sheet_square_size=24

drawArena(arena,sprite_sheet,sprite_id,sprite_sheet_column_count,sprite_sheet_square_size)
