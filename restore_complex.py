import numpy as np
import os

import utils
from sphere_fibonacci_grid_points import sphere_fibonacci_grid_points
from config import *
from MyMesh import MyMesh

def rotateToZaxis(points, plane):
    basis = utils.get2dBasis(plane).T
    s_coord = utils.appendSpherical_np(np.array([plane])).squeeze()
    rotation = np.matmul(utils.rotateAxisZ(-s_coord[5]), utils.rotateAxisY(-s_coord[4]))
    return (
        np.matmul(basis, rotation),
        np.matmul(points, rotation)
    )

def rotateBasis(points, basis):
    # print(np.dot(basis[0], basis[1]))
    # print(np.dot(np.cross(basis[1], basis[0]), np.array([0, 0, 1])))
    s_coord = utils.appendSpherical_np(np.array([basis[0]])).squeeze()
    print(s_coord)

    rotation = utils.rotateAxisZ(-s_coord[5])

    return np.matmul(points, rotation)

    # print(np.matmul(basis, rotation))

    # rotation = np.matmul(utils.rotateAxisZ(-s_coord[5]), utils.rotateAxisY(-s_coord[4]))

def rotatePoints(points, angle):
    return np.matmul(points, utils.rotateAxisZ(angle))

def flipPoints(points):
    return np.matmul(points, utils.rotateAxisX(np.pi))

def offsetPoint(points, direction):
    return points + direction

def restore_query_target(query, target, height, offset, rotation, step = 1):
    fibosphere = sphere_fibonacci_grid_points(CONF["n_fibo"])
    target_fib_id = rotation[0] * step
    target_rot_id = rotation[1]
    target_rot_angle = target_rot_id * (2 * np.pi / (CONF["n_rot"] / step))
    query_fib_id = rotation[2] * step
    query_rot_id = rotation[3]
    query_rot_angle = query_rot_id * (2 * np.pi / (CONF["n_rot"] / step))
    offset = np.array([offset[1], offset[0], height - query.radius - target.radius])
    basis, query.vertices = rotateToZaxis(query.vertices, fibosphere[query_fib_id])
    query.vertices = rotateBasis(query.vertices, basis)
    query.vertices = rotatePoints(query.vertices, query_rot_angle)
    query.vertices = flipPoints(query.vertices)
    query.vertices = offsetPoint(query.vertices, offset)

    basis, target.vertices = rotateToZaxis(target.vertices, fibosphere[target_fib_id])
    target.vertices = rotateBasis(target.vertices, basis)
    target.vertices = rotatePoints(target.vertices, target_rot_angle)

    query_path = os.path.join(COMPLEXES_PATH_PREFIX, f"query_{3}.ply")
    query.save(query_path)
    target_path = os.path.join(COMPLEXES_PATH_PREFIX, f"target_{3}.ply")
    target.save(target_path)

def restore(query_id, step = 1):
    path = os.path.join(STATES_PATH_PREFIX, MESH_CONF["query"]["result"], f"{query_id}.npy")
    with open(path, "rb") as fi:
        query_sch = np.load(fi)
        query_sco, query_hei = query_sch[:,0], query_sch[:,1]
        query_off = np.load(fi)
        query_rot = np.load(fi)

    # print(query_sco)
    top_10 = utils.get_top_k(query_sco, 1, axis=0)
    # print(query_sco[top_10[0]])

    for target_id in top_10:
        query = MyMesh(os.path.join(PATH_PREFIX, MESH_CONF["query"]["type"], f"{query_id}.ply"))
        target = MyMesh(os.path.join(PATH_PREFIX, MESH_CONF["target"]["type"], f"{target_id}.ply"))
        restore_query_target(query, target, query_hei[target_id], query_off[target_id], query_rot[target_id], step)

def main():
    # a = np.array([9, 4, 4, 3, 3, 9, 0, 4, 6, 0])
    # ind = np.argpartition(a, -4)
    # print(ind)

    restore(3, 2)


if __name__ == "__main__":
    main()