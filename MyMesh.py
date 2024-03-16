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
    
    def meshSimilarity(self, other):
        assert self.states != None
        assert other.states != None

        def tableComplementary(tabA, tabB):
            pass 

        def tableSimilarity(tabA, tabB):
            # tabA = np.sum(np.multiply(tabA, tabA), axis=2)
            # tabB = np.sum(np.multiply(tabB, tabB), axis=2)

            # diff = tabA - tabB
            # diff = np.multiply(diff, diff)
            # diff = diff[np.isfinite(diff)]
            
            # diff 

            diff = tabA - tabB
            diff = np.multiply(diff, diff)
            diff = diff[np.isfinite(diff)]

            



        for tabA in self.states:
            for tabB in other.states:
                pass