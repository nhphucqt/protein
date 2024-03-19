import os
import numpy as np
from plyfile import PlyData, PlyElement
from sphere_fibonacci_grid_points import sphere_fibonacci_grid_points
import json

import utils

from MyMesh import MyMesh
from config import *

ptype = MESH_CONF["target"]

def info_ptype(ptype):
    print(ptype)
    
def readMesh(ptype, id):
    assert id < ptype["num"]
    return MyMesh(os.path.join(PATH_PREFIX, os.path.join(ptype["type"], f"{id}.ply")))

def convert_text_to_bin(ptype, destination, start_id = 0):
    info_ptype(ptype)
    path = os.path.join(PATH_PREFIX, ptype["type"])
    print("Path:", path)
    for i in range(start_id, ptype["num"]):
        filename = f"{i}.ply"
        print("Reading mesh", i, '...')
        plydata = PlyData.read(os.path.join(path, filename), known_list_len={'face': {'vertex_indices': 3}})
        
        plydata.text = False
        plydata.byte_order = "<"
        print("Writing mesh ...")
        plydata.write(os.path.join(destination, filename))

def save_mesh_state(ptype, start_id = 0, end_id = -1):
    info_ptype(ptype)
    if end_id == -1:
        end_id = ptype["num"]
    # create folder
    if not os.path.exists(os.path.join(PATH_PREFIX, ptype["state"])):
        os.makedirs(os.path.join(PATH_PREFIX, ptype["state"]))

    fibosphere = sphere_fibonacci_grid_points(CONF["n_fibo"])
    for i in range(start_id, end_id):
        print(f"Mesh {i} (from {start_id} to {end_id})...")

        mesh = readMesh(ptype, i)

        states = []
        cnt = 0

        for fib in fibosphere:
            cnt += 1
            print(cnt, "rotation...")
            states.append(get_height_matrix(mesh, fib))

        states = np.array(states)
        
        with open(os.path.join(os.path.join(PATH_PREFIX, ptype["state"]), f"{i}.json"), "w") as fo:
            json.dump(CONF, fo, indent=2)
        
        with open(os.path.join(os.path.join(PATH_PREFIX, ptype["state"]), f"{i}.npy"), "wb") as fo:
            np.save(fo, states)


def get_height_matrix(mesh, plane): # plane is a unit vector
    vertices = mesh.getVertexList() + (plane * mesh.radius)

    heights = np.abs(np.dot(vertices, plane))

    projection = vertices - plane * np.vstack(heights)
    
    basis = utils.get2dBasis(plane)

    newPoints = np.matmul(projection, basis)

    mat_shape = tuple([CONF["n_rot"]]) + CONF["h_mat_shape"]
    height_mat = np.full(shape=mat_shape, fill_value=-np.inf)

    for rot in range(CONF["n_rot"]):
        a = rot * (2*np.pi/CONF["n_rot"])
        rotPoints = np.matmul(newPoints, utils.rotate2d(a))
        for p, h in zip(rotPoints, heights):
            x = min(mat_shape[1]-1, max(0, int(np.rint(p[0] + mat_shape[1]/2))))
            y = min(mat_shape[2]-1, max(0, int(np.rint(p[1] + mat_shape[2]/2))))
            height_mat[rot,y,x] = max(height_mat[rot,y,x], h)

    return height_mat

save_mesh_state(MESH_CONF["query"])
save_mesh_state(MESH_CONF["target"])