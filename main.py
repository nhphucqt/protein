import os
import numpy as np
from plyfile import PlyData, PlyElement
from sphere_fibonacci_grid_points import sphere_fibonacci_grid_points
import json

# PATH_PREFIX = "/media/nhphucqt/NHPHUCQT/Research/shrec2024/protein"
PATH_PREFIX = "/home/nhphucqt/Documents/MyLabs/protein"

MESH_CONF = {
    "query": {
        "num": 387,
        "type": "queries_bin",
        "save": "queries_states"
    },
    "target": {
        "num": 520,
        "type": "targets_bin",
        "save": "targets_states"
    }
}
ptype = MESH_CONF["query"]

CONF = {
    "n_fibo": 24,
    "n_rot": 16,
    "h_mat_shape": (100, 100)
}

def info_ptype(ptype):
    print(ptype)

class MyMesh:
    def __init__(self, path):
        self.mesh = PlyData.read(path, known_list_len={'face': {'vertex_indices': 3}})
        self.vertices = np.array(self.mesh["vertex"].data.tolist())[:,:3]
        centroid = np.mean(self.vertices, axis=0)
        self.vertices -= centroid
        self.radius = np.max(np.linalg.norm(self.vertices, axis=1))


    def getFaceVertices(self, face):
        return np.array([self.mesh["vertex"][i].tolist()[:3] for i in face["vertex_indices"]])

    def getFaceVertices_id(self, id):
        assert id < self.mesh["face"].count
        return self.getFaceVertices(self.mesh["face"][id])
    
    def faceArea(self, face):
        vertices = self.getFaceVertices(face)
        norm = np.cross(vertices[2] - vertices[0], vertices[1] - vertices[0])
        return np.sqrt(np.dot(norm, norm)) / 2.0
    
    def faceArea_id(self, id):
        assert id < self.mesh["face"].count
        return self.faceArea(self.mesh["face"][id])
    
    def allFaceArea(self):
        vertices = np.array([self.getFaceVertices(face) for face in self.mesh['face']])
        a = np.cross(vertices[:,1] - vertices[:,0], vertices[:,2] - vertices[:,0])
        res = np.sqrt((a*a).sum(1)) / 2.0
        return res
    
    def getVertexList(self):
        return self.vertices
    
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

def list_faces_area(ptype):
    areas = []
    for i in range(ptype["num"]):
        print("Mesh", i)
        mesh = readMesh(ptype, i)
        a = mesh.allFaceArea()
        print(np.min(a), np.max(a), np.mean(a))
        areas.append([np.min(a), np.max(a), np.mean(a)])
    print(areas)
    
def min_max_coord(ptype):
    fibosphere = sphere_fibonacci_grid_points(CONF["n_fibo"])
    heights = []
    for i in range(ptype["num"]):
        print("Mesh", i)
        mesh = readMesh(ptype, i)
        heights.append(np.max([get_height_matrix(mesh, fi) for fi in fibosphere]))
        print(heights[-1])
    print(">>", np.max(heights))

def save_mesh_state(ptype):
    fibosphere = sphere_fibonacci_grid_points(CONF["n_fibo"])
    for i in range(ptype["num"]):
        print("Mesh", i, "...")

        mesh = readMesh(ptype, i)

        states = []
        cnt = 0

        for fib in fibosphere:
            cnt += 1
            print(cnt, "rotation...")
            states.append(get_height_matrix(mesh, fib))

        states = np.array(states)
        
        with open(os.path.join(os.path.join(PATH_PREFIX, ptype["save"]), f"{i}.json"), "w") as fo:
            json.dump(CONF, fo, indent=2)
        
        with open(os.path.join(os.path.join(PATH_PREFIX, ptype["save"]), f"{i}.npy"), "wb") as fo:
            np.save(fo, states)


def get_height_matrix(mesh, plane): # plane is a unit vector
    vertices = mesh.getVertexList() + (plane * mesh.radius)

    heights = np.abs(np.dot(vertices, plane))

    projection = vertices - plane * np.vstack(heights)
    
    axisX = np.array([-plane[1], plane[0], 0])
    axisY = np.cross(plane, axisX)
    basis = np.dstack((axisX, axisY))

    newPoints = np.matmul(projection, basis).squeeze()

    mat_shape = tuple([CONF["n_rot"]]) + CONF["h_mat_shape"]
    height_mat = np.full(shape=mat_shape, fill_value=-np.inf)

    for rot in range(CONF["n_rot"]):
        a = rot * 2*np.pi/CONF["n_rot"]
        rotPoints = np.matmul(newPoints, np.array([[np.cos(a), np.sin(a)], [-np.sin(a), np.cos(a)]]))
        for p, h in zip(rotPoints, heights):
            x = min(mat_shape[0]-1, max(0, int(p[0] + mat_shape[0]/2)))
            y = min(mat_shape[1]-1, max(0, int(p[1] + mat_shape[1]/2)))
            height_mat[rot,y,x] = max(height_mat[rot,y,x], h)

    return height_mat

# des

mesh = readMesh(ptype, 0);
fibosphere = sphere_fibonacci_grid_points(CONF["n_fibo"])
save_mesh_state(ptype)

# convert_text_to_bin(ptype, os.path.join(PATH_PREFIX, f"/home/nhphucqt/Documents/MyLabs/protein/{ptype['type']}_bin"))

# arr = np.array(list(map(tuple, arr.tolist())), dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
# el = PlyElement.describe(arr, "vertex", val_types={'x': 'f4', 'y': 'f4', 'z': 'f4'})
# # print(el)
# mesh = PlyData([el], text=True)
# print(mesh)
# mesh.write("fibosphere.ply")
    