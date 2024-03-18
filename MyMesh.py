import numpy as np
from plyfile import PlyData, PlyElement

class MyMesh:
    def __init__(self, path):
        self.mesh = PlyData.read(path, known_list_len={'face': {'vertex_indices': 3}})
        self.vertices = np.array(self.mesh["vertex"].data.tolist())[:,:3]
        centroid = np.mean(self.vertices, axis=0)
        self.vertices -= centroid
        self.radius = np.max(np.linalg.norm(self.vertices, axis=1))
        self.states = None

    def loadState(self, path):
        self.state = np.load(path)

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
    
    def save(self, path):
        # self.mesh["vertex"].data = self.vertices
        # self.mesh.text = False
        # self.mesh.byte_order = "<"
        # self.mesh.write(path)
        # self.mesh.write(path)

        vertex = np.array(list(map(tuple, self.vertices.tolist())), dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4')])
        el_vertex = PlyElement.describe(vertex, "vertex", val_types={'x': 'f4', 'y': 'f4', 'z': 'f4'})

        # face = [face["vertex_indices"] for face in self.mesh["face"]]
        # print(face)

        # print(self.mesh["face"].data["vertex_indices"])

        # face = np.array(list(map(tuple, self.mesh["face"].data["vertex_indices"].tolist())))

        # print(tuple([[3,4]]))

        face = np.array(list(map(lambda x: tuple([x]), self.mesh["face"].data["vertex_indices"].tolist())), dtype=[('vertex_indices', 'i4', (3,))])
        print(face)
        el_face = PlyElement.describe(face, "face", val_types={'vertex_indices': 'i4'})
        mesh = PlyData([el_vertex, el_face], text=True)
        # # print(mesh)
        mesh.write(path)