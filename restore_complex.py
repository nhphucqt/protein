import numpy as np
import os
import sys

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
    s_coord = utils.appendSpherical_np(np.array([basis[0]])).squeeze()
    rotation = utils.rotateAxisZ(-s_coord[5])
    return np.matmul(points, rotation)

def rotatePoints(points, angle):
    return np.matmul(points, utils.rotateAxisZ(angle))

def flipPoints(points):
    return np.matmul(points, utils.rotateAxisX(np.pi))

def offsetPoint(points, direction):
    return points + direction

def restore_query_target(query_id, target_id, height, offset, rotation, step = 1):
    query = MyMesh(os.path.join(PATH_PREFIX, MESH_CONF["query"]["type"], f"{query_id}.ply"))
    target = MyMesh(os.path.join(PATH_PREFIX, MESH_CONF["target"]["type"], f"{target_id}.ply"))

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

    # query_path = os.path.join(COMPLEXES_PATH_PREFIX, f"query_{query_id}.ply")
    # query.save(query_path)
    # target_path = os.path.join(COMPLEXES_PATH_PREFIX, f"target_{query_id}.ply")
    # target.save(target_path)

    merged = MyMesh.mergeMesh(query, target)
    merged_path = os.path.join(COMPLEXES_PATH_PREFIX, f"{query_id}_{target_id}.ply")
    MyMesh.savePly(merged[0], merged[1], merged_path)

def restore(query_id, step = 1):
    path = os.path.join(STATES_PATH_PREFIX, MESH_CONF["query"]["result"], f"{query_id}.npy")
    with open(path, "rb") as fi:
        query_sch = np.load(fi)
        query_sco, query_hei = query_sch[:,0], query_sch[:,1]
        query_off = np.load(fi)
        query_rot = np.load(fi)

    top_10 = utils.get_top_k(query_sco, 10, axis=0)
    print(top_10)

    for target_id in top_10:
        restore_query_target(query_id, target_id, query_hei[target_id], query_off[target_id], query_rot[target_id], step)

def restore_all(start_id, end_id, step = 1):
    for i in range(start_id, end_id):
        print(f"Restore {i} ({start_id} - {end_id})...")
        restore(i, step)

def main():
    range_id = int(sys.argv[1])
    start_id, end_id = RANGE_QUERIES[range_id]
    restore_all(start_id, end_id, 2)

if __name__ == "__main__":
    main()