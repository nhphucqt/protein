import numpy as np
import os

from config import *

def get_matrix_score():
    score_matrix = []
    for query_id in range(MESH_CONF["query"]["num"]):
        path = os.path.join(STATES_PATH_PREFIX, MESH_CONF["query"]["result"], f"{query_id}.npy")
        with open(path, "rb") as fi:
            query_sch = np.load(fi)
            query_sco, query_hei = query_sch[:,0], query_sch[:,1]
        score_matrix.append(query_sco)
    return np.array(score_matrix)

def main():
    np.save(SCORE_MATRIX_PATH, get_matrix_score())

if __name__ == "__main__":
    main()

    # with open(SCORE_MATRIX_PATH, "rb") as fi:
    #     score_matrix = np.load(fi)
    #     print(score_matrix.shape)