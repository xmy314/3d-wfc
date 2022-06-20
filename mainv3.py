import os
from os import path
import numpy as np

from obj_loader import read_obj, write_obj
from symmetry_generation_3 import SymmetryGroup, Cube,Face
from wfc_solver import solveWFC,extendConstraints

from datetime import datetime


collapse_count=500

symmetry_of_label={
    "c":SymmetryGroup.ref_orth,
    "t":SymmetryGroup.ref_by_y,
    "a":SymmetryGroup.all_symmetry,
    "l":SymmetryGroup.ref_by_major,
    "st":SymmetryGroup.ref_by_major,
    "d":SymmetryGroup.ref_orth,
}

starting_time=datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
print( f"started at : {starting_time}")

def decipher_file_name(name):
    decoded=[]
    current_label=""
    current_orientation=0

    for character in name:
        if character == "-" or character == ".":
            decoded.append((current_label,current_orientation))
            current_label=""
            current_orientation=0
            if character==".":
                return decoded
        elif character.isnumeric():
            current_orientation=int(character)
        else :
            current_label+=character
            

# load the informations
module_filenames = list(filter(lambda x:x.split(".")[-1]=="obj", os.listdir("3d modules")))
# mesh is for final visualization
module_meshes = [read_obj(path.join("3d modules",x)) for x  in module_filenames]
# modules are for automatically generating constraints
modules = []
for mesh_id,module_filename in enumerate(module_filenames):
    a=decipher_file_name(module_filename)
    
    cube_prototype = Cube(
                        *zip(*((x[0],symmetry_of_label[x[0]],x[1]) for x in a)),
                        mesh_id)
    
    modules+=cube_prototype.generateVariations()


# generate very local constraints that can be determined by only comparing the faces.
import pickle

# all_module_set=set(range(len(modules)))
# raw_constraints={}
# for module_a_id, module_a in enumerate(modules):
#     raw_constraints[module_a_id]={}

#     for module_b_id, module_b in enumerate(modules):

#         for b_rel_a,compared_faces in [((1,0,0),(0,3)),((0,1,0),(1,4)),((0,0,1),(2,5))]:
#             if not Face.match(module_a.faces[compared_faces[0]],module_b.faces[compared_faces[1]]):
#                 if not b_rel_a in raw_constraints[module_a_id]:
#                     raw_constraints[module_a_id][b_rel_a] = all_module_set.copy()
#                 raw_constraints[module_a_id][b_rel_a].remove(module_b_id)

# extended_constraints=extendConstraints(raw_constraints,all_module_set,(0,0,0))

# with open('saved_dictionary.pkl', 'wb') as f:
#     pickle.dump(extended_constraints, f)

with open('saved_dictionary.pkl', 'rb') as f:
    extended_constraints = pickle.load(f)

# pass these constraints into the solver to have it solved
arena=solveWFC(extended_constraints,collapse_count,True)
# render/generate a combined mesh for the result.
result_verts=[]
result_faces=[]
id_off_set=0
for position in arena:
    if (len(arena[position])!=1): continue # this checks whether the possibility has been collapsed

    for module_id in arena[position]:break
    
    module_at_position = modules[module_id]

    id_off_set=len(result_verts)

    verts_at_position,faces_at_position = module_meshes[module_at_position.mesh_id]
    
    translation_matrix = np.asarray(
        [
            [1,0,0,position[0]],
            [0,1,0,position[1]],
            [0,0,1,position[2]],
            [0,0,0,1],
        ]
    )

    loop_direction = -1 if module_at_position.reflected else 1

    transformed_verts = np.matmul(
        translation_matrix, 
        np.matmul(
            module_at_position.transformation,
            np.pad(verts_at_position, ((0,1),(0,0)), 'constant', constant_values=1)))[:3]
    
    result_verts+=transformed_verts.T.tolist()
    result_faces+=[[v+id_off_set for v in face[::loop_direction]] for face in faces_at_position]

outputh_path="output3"
output_name=f"{starting_time}-{collapse_count}.obj"

write_obj(path.join(outputh_path,output_name),(result_verts,result_faces))

# snakeviz /tmp/tmp.prof