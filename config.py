# PATH_PREFIX = "/media/nhphucqt/NHPHUCQT/Research/shrec2024/protein"

# PATH_PREFIX = "/home/nhphucqt/Documents/MyLabs/protein"
PATH_PREFIX = "/root/dataset"
# STATES_PATH_PREFIX = "/media/nhphucqt/NHPHUCQT/Research/shrec2024/protein/states.1.0/dataset_states/"
# COMPLEXES_PATH_PREFIX = "/media/nhphucqt/NHPHUCQT/Research/shrec2024/protein/complexes/"
COMPLEXES_PATH_PREFIX = "/root/complexes"
STATES_PATH_PREFIX = "/root/dataset_states"
# STATES_PATH_PREFIX = "/kaggle/input/dataset_states"

MESH_CONF = {
    "query": {
        "num": 387,
        "type": "queries_bin",
        "state": "queries_states",
        "decimate": "queries_bin_dec",
        "result": "results"
    },
    "target": {
        "num": 520,
        "type": "targets_bin",
        "state": "targets_states",
        "decimate": "targets_bin_dec"
    }
}

CONF = {
    "n_fibo": 24,
    "n_rot": 16,
    "h_mat_shape": (100, 100)
}

# 0 to 10
RANGE_ID = 0

RANGE_QUERIES = [
    (0, 35),
    (35, 70),
    (70, 105),
    (105, 140),
    (140, 175),
    (175, 210),
    (210, 245),
    (245, 280),
    (280, 315),
    (315, 350),
    (350, 387)
]

RANGE_TARGETS = [
    (0, 47),
    (47, 94),
    (94, 141),
    (141, 188),
    (188, 235),
    (235, 282),
    (282, 329),
    (329, 376),
    (376, 423),
    (423, 470),
    (470, 520)
]