import numpy as np

import utils
from sphere_fibonacci_grid_points import sphere_fibonacci_grid_points
from config import *

def rotateToZaxis(points, plane):
    basis = utils.get2dBasis(plane).T
    s_coord = utils.appendSpherical_np(np.array([plane])).squeeze()
    rotation = np.matmul(utils.rotateAxisZ(-s_coord[5]), utils.rotateAxisY(-s_coord[4]))
    print(np.matmul(np.array([plane]), rotation))
    return (
        np.matmul(basis, rotation),
        np.matmul(points, rotation)
    )

def rotateBasis(points, basis):
    a = basis[0] / np.linalg.norm(basis[0])
    print(np.dot(a, a))
    print(np.dot(basis[0], basis[0]))
    # print(np.dot(np.cross(basis[1], basis[0]), np.array([0, 0, 1])))
    # s_coord = utils.appendSpherical_np(np.array([basis[0]])).squeeze()
    # print(s_coord)
    # rotation = np.matmul(utils.rotateAxisZ(-s_coord[5]), utils.rotateAxisY(-s_coord[4]))



def main():
    fibosphere = sphere_fibonacci_grid_points(CONF["n_fibo"])
    points = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
    basis, points = rotateToZaxis(points, fibosphere[0])
    print(basis)
    rotateBasis(points, basis)


if __name__ == "__main__":
    main()