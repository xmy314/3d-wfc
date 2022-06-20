import re
import numpy as np

def read_obj(path):

    tokenizer = re.compile(r"^(v|f)\s+(((?:\/*-?\d+(?:\.\d+)?e?)*\s?)+)$")
    verts = []
    faces = []
    with open(path, "r") as fi:
        while True:
            text_input = fi.readline()
            if not text_input:
                break
            match = tokenizer.match(text_input)
            if match:
                instruction = match.group(1)
                content = match.group(2)
                if instruction == "v":
                    verts.append([float(x) for x in content.split()])
                elif instruction == "f":
                    faces.append([int(x.split("/")[0]) for x in content.split()])
    # 1 indexing from .obj to 0 indexing in other
    faces=[[vid-1 for vid in face] for face in faces]
    if verts==[]:
        verts=np.zeros((3,0))
    else:
        verts=np.asarray(verts).T
    return (verts,faces)

def write_obj(path,mesh_information):
    verts,faces = mesh_information
    with open(path, "w+") as fi:
        for vert in verts:
            fi.write("v "+" ".join([str(x) for x in vert])+ "\n")

        for face in faces:
            fi.write("f "+" ".join([str(x+1) for x in face])+ "\n")




    
